from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.core.exceptions import NotFoundException
from backend.app.models.inspection import (
    Inspection,
    InspectionStatus,
    InspectionImage,
    InspectionResult,
    Defect,
    InspectionReview,
    ReviewDecision,
)
from backend.app.schemas.inspection import HumanReviewRequest


class InspectionRepository:
    """Repository handling tenant-isolated persistence for visual inspection sessions and results."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id_and_org(self, inspection_id: str, org_id: str) -> Optional[Inspection]:
        return (
            self.db.query(Inspection)
            .filter(Inspection.id == inspection_id, Inspection.organization_id == org_id)
            .first()
        )

    def list_inspections(
        self,
        org_id: str,
        product_id: Optional[str] = None,
        status: Optional[InspectionStatus] = None,
        is_defective: Optional[bool] = None,
        batch_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Inspection]:
        stmt = self.db.query(Inspection).filter(Inspection.organization_id == org_id)

        if product_id:
            stmt = stmt.filter(Inspection.product_id == product_id)
        if status:
            stmt = stmt.filter(Inspection.status == status)
        if batch_id:
            stmt = stmt.filter(Inspection.batch_id == batch_id)
        if is_defective is not None:
            stmt = stmt.join(Inspection.result).filter(InspectionResult.is_defective == is_defective)

        return stmt.order_by(desc(Inspection.created_at)).offset(skip).limit(limit).all()

    def create_inspection(
        self,
        org_id: str,
        product_id: str,
        inspector_id: Optional[str] = None,
        batch_id: Optional[str] = None,
    ) -> Inspection:
        inspection = Inspection(
            organization_id=org_id,
            product_id=product_id,
            inspector_id=inspector_id,
            status=InspectionStatus.QUEUED,
            batch_id=batch_id,
        )
        self.db.add(inspection)
        self.db.commit()
        self.db.refresh(inspection)
        return inspection

    def attach_image(
        self,
        inspection: Inspection,
        storage_key: str,
        original_filename: str,
        metadata: Dict[str, Any],
    ) -> InspectionImage:
        image = InspectionImage(
            inspection_id=inspection.id,
            storage_key=storage_key,
            original_filename=original_filename,
            file_size_bytes=metadata["size_bytes"],
            width=metadata["width"],
            height=metadata["height"],
            mime_type=metadata["mime_type"],
            checksum_sha256=metadata["checksum_sha256"],
        )
        self.db.add(image)
        self.db.commit()
        self.db.refresh(inspection)
        return image

    def attach_result(
        self,
        inspection: Inspection,
        model_name: str,
        model_version: str,
        predicted_class: str,
        confidence: float,
        is_defective: bool,
        anomaly_score: Optional[float] = None,
        inference_time_ms: int = 0,
        defects_list: Optional[List[Dict[str, Any]]] = None,
        requires_review_threshold: float = 0.70,
    ) -> InspectionResult:
        result = InspectionResult(
            inspection_id=inspection.id,
            model_name=model_name,
            model_version=model_version,
            predicted_class=predicted_class,
            confidence=confidence,
            is_defective=is_defective,
            anomaly_score=anomaly_score,
            inference_time_ms=inference_time_ms,
        )
        self.db.add(result)
        self.db.flush()

        if defects_list:
            for d in defects_list:
                defect = Defect(
                    result_id=result.id,
                    defect_type=d.get("defect_type", predicted_class),
                    severity=d.get("severity", "MEDIUM"),
                    bbox_x=d.get("bbox_x"),
                    bbox_y=d.get("bbox_y"),
                    bbox_w=d.get("bbox_w"),
                    bbox_h=d.get("bbox_h"),
                    confidence=d.get("confidence", confidence),
                )
                self.db.add(defect)

        # Update inspection status: if confidence is below threshold, flag as REQUIRES_REVIEW
        if confidence < requires_review_threshold:
            inspection.status = InspectionStatus.REQUIRES_REVIEW
        else:
            inspection.status = InspectionStatus.COMPLETED

        self.db.commit()
        self.db.refresh(inspection)
        return result

    def record_failure(self, inspection: Inspection, error_msg: str) -> None:
        inspection.status = InspectionStatus.FAILED
        inspection.error_message = error_msg[:1000]
        self.db.commit()

    def add_human_review(
        self,
        inspection: Inspection,
        reviewer_id: str,
        payload: HumanReviewRequest,
    ) -> InspectionReview:
        # Check if already reviewed
        existing_review = (
            self.db.query(InspectionReview)
            .filter(InspectionReview.inspection_id == inspection.id)
            .first()
        )
        if existing_review:
            existing_review.reviewer_id = reviewer_id
            existing_review.decision = payload.decision
            existing_review.final_class = payload.final_class
            existing_review.is_defective = payload.is_defective
            existing_review.notes = payload.notes
            self.db.commit()
            self.db.refresh(existing_review)
            return existing_review

        review = InspectionReview(
            inspection_id=inspection.id,
            reviewer_id=reviewer_id,
            decision=payload.decision,
            final_class=payload.final_class,
            is_defective=payload.is_defective,
            notes=payload.notes,
        )
        self.db.add(review)

        # Once human review is signed off, set status to COMPLETED
        inspection.status = InspectionStatus.COMPLETED
        self.db.commit()
        self.db.refresh(inspection)
        return review
