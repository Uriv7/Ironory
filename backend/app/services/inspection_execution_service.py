"""Automated AI Inspection Execution Service for Ironory.

Executes deep learning inference on uploaded inspection visual assets,
extracts defect localization and Grad-CAM explainability maps, and persists
results in tenant-isolated database tables.
"""

from __future__ import annotations

import io
import logging
from typing import Optional
from PIL import Image
from sqlalchemy.orm import Session

from backend.app.models.inspection import Inspection, InspectionStatus
from backend.app.repositories.inspection_repository import InspectionRepository
from backend.app.repositories.product_repository import ProductRepository
from backend.app.services.storage import get_storage_service
from ml.inference.service import get_inference_engine

logger = logging.getLogger("ironory.backend.services.inspection_execution")


class InspectionExecutionService:
    """Service orchestrating AI inference execution for inspection sessions."""

    @classmethod
    def execute_inspection(cls, inspection_id: str, org_id: str, db: Session) -> Inspection:
        """Run deep learning inspection on uploaded image and persist results."""
        inspection_repo = InspectionRepository(db)
        inspection = inspection_repo.get_by_id_and_org(inspection_id, org_id)
        if not inspection:
            raise ValueError(f"Inspection '{inspection_id}' not found.")

        if not inspection.image:
            inspection_repo.record_failure(inspection, "Inspection has no attached image asset.")
            return inspection

        product_repo = ProductRepository(db)
        product = product_repo.get_by_id_and_org(inspection.product_id, org_id)

        # Determine configured model and threshold
        model_name = "baseline_cnn"
        confidence_threshold = 0.70

        if product and product.inspection_config:
            cfg = product.inspection_config
            if cfg.primary_model:
                raw_model = cfg.primary_model.lower().replace("-", "_").replace(" ", "_")
                if "mobilenet" in raw_model:
                    model_name = "mobilenet_v2"
                elif "efficientnet" in raw_model:
                    model_name = "efficientnet_b0"
                else:
                    model_name = "baseline_cnn"
            if cfg.defect_threshold is not None:
                confidence_threshold = float(cfg.defect_threshold)

        # Retrieve image bytes from storage
        storage = get_storage_service()
        try:
            image_bytes = storage.get(inspection.image.storage_key)
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            logger.error(f"Failed to read image asset from storage: {e}")
            inspection_repo.record_failure(inspection, f"Failed to retrieve image asset: {e}")
            return inspection

        # Execute deep learning inference
        engine = get_inference_engine()
        try:
            inference_result = engine.run_inference(
                image_input=pil_img,
                model_name=model_name,
                confidence_threshold=confidence_threshold,
                generate_xai=True,
            )
        except Exception as e:
            logger.error(f"Inference execution failed: {e}")
            inspection_repo.record_failure(inspection, f"AI Model execution error: {e}")
            return inspection

        # Format defects list from detected localization boxes
        defects_list = []
        for box in inference_result.bounding_boxes:
            severity = "HIGH" if inference_result.confidence > 0.85 else "MEDIUM"
            defects_list.append({
                "defect_type": box.get("label", inference_result.predicted_class),
                "severity": severity,
                "bbox_x": box.get("x_min"),
                "bbox_y": box.get("y_min"),
                "bbox_w": box.get("width"),
                "bbox_h": box.get("height"),
                "confidence": box.get("confidence", inference_result.confidence),
            })

        # Persist Grad-CAM overlay if available
        if inference_result.overlay_image:
            try:
                overlay_buf = io.BytesIO()
                inference_result.overlay_image.save(overlay_buf, format="JPEG", quality=90)
                overlay_buf.seek(0)
                overlay_key = storage.save(
                    file_obj=overlay_buf,
                    tenant_id=org_id,
                    original_filename=f"{inspection.id}_gradcam_overlay.jpg",
                    subfolder="overlays",
                )
                logger.info(f"Saved Grad-CAM overlay to storage: {overlay_key}")
            except Exception as e:
                logger.warning(f"Could not persist Grad-CAM overlay: {e}")

        # Attach persisted result to inspection record
        inspection_repo.attach_result(
            inspection=inspection,
            model_name=inference_result.model_name,
            model_version=inference_result.model_version,
            predicted_class=inference_result.predicted_class,
            confidence=inference_result.confidence,
            is_defective=inference_result.is_defective,
            anomaly_score=inference_result.anomaly_score,
            inference_time_ms=int(inference_result.inference_time_ms),
            defects_list=defects_list,
            requires_review_threshold=confidence_threshold,
        )

        logger.info(
            f"Inspection {inspection.id} completed: class={inference_result.predicted_class}, "
            f"confidence={inference_result.confidence}, status={inspection.status}"
        )
        return inspection
