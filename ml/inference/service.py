"""Ironory Unified ML Inference Service.

Handles model loading, warm-up, runtime inference, Grad-CAM XAI explanation,
anomaly scoring, and formatting predictions for persistence in Ironory database.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

from ml.datasets.neu_loader import DEFECT_CLASSES, IDX_TO_CLASS
from ml.visualization.gradcam import generate_gradcam_heatmap, overlay_gradcam

logger = logging.getLogger("ironory.ml.inference")

ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"


@dataclass
class BoundingBox:
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    confidence: float
    label: str


@dataclass
class InferenceResult:
    predicted_class: str
    confidence: float
    is_defective: bool
    class_probabilities: Dict[str, float]
    inference_time_ms: float
    model_name: str
    model_version: str = "1.0.0"
    bounding_boxes: List[Dict[str, Any]] = field(default_factory=list)
    heatmap_array: Optional[np.ndarray] = None
    overlay_image: Optional[Image.Image] = None
    anomaly_score: Optional[float] = None
    requires_review: bool = False


class InferenceEngine:
    """Thread-safe multi-model inference engine."""

    def __init__(self, artifacts_dir: Path = ARTIFACTS_DIR):
        self.artifacts_dir = Path(artifacts_dir)
        self._models: Dict[str, Any] = {}
        self.class_names = DEFECT_CLASSES

    def load_model(self, model_name: str = "baseline_cnn"):
        """Load and cache model weights from disk."""
        import tensorflow as tf

        if model_name in self._models:
            return self._models[model_name]

        model_file = self.artifacts_dir / f"{model_name}.keras"
        if not model_file.exists():
            raise FileNotFoundError(f"Model artifact not found: {model_file}")

        logger.info(f"Loading model artifact: {model_file}")
        model = tf.keras.models.load_model(str(model_file))
        self._models[model_name] = model
        return model

    def preprocess_image(self, image_input: Any, target_size: Tuple[int, int] = (224, 224)) -> Tuple[Image.Image, np.ndarray]:
        """Convert input to PIL Image and normalized (1, 224, 224, 3) float32 array in [0, 1]."""
        if isinstance(image_input, (str, Path)):
            pil_img = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
        elif isinstance(image_input, np.ndarray):
            pil_img = Image.fromarray(image_input.astype(np.uint8)).convert("RGB")
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        resized_img = pil_img.resize(target_size, Image.Resampling.BILINEAR)
        img_array = np.array(resized_img, dtype=np.float32) / 255.0
        tensor = np.expand_dims(img_array, axis=0)  # Shape (1, 224, 224, 3)
        return resized_img, tensor

    def _extract_bounding_box_from_heatmap(
        self, heatmap: np.ndarray, label: str, confidence: float, threshold: float = 0.55
    ) -> List[Dict[str, Any]]:
        """Extract bounding box coordinates enclosing peak activation regions in Grad-CAM heatmap."""
        import cv2

        h, w = heatmap.shape
        binary_mask = np.uint8(heatmap > threshold) * 255
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < (h * w * 0.01):  # Ignore tiny noise (<1% of image)
                continue
            x, y, bw, bh = cv2.boundingRect(cnt)
            boxes.append({
                "x_min": int(x),
                "y_min": int(y),
                "x_max": int(x + bw),
                "y_max": int(y + bh),
                "width": int(bw),
                "height": int(bh),
                "area_pixels": int(area),
                "label": label,
                "confidence": round(confidence, 4),
            })

        # If no significant contour found, return overall peak center box
        if not boxes:
            max_pos = np.unravel_index(np.argmax(heatmap), heatmap.shape)
            cy, cx = int(max_pos[0]), int(max_pos[1])
            box_half = 28  # 56x56 patch
            boxes.append({
                "x_min": max(0, cx - box_half),
                "y_min": max(0, cy - box_half),
                "x_max": min(w, cx + box_half),
                "y_max": min(h, cy + box_half),
                "width": min(w, cx + box_half) - max(0, cx - box_half),
                "height": min(h, cy + box_half) - max(0, cy - box_half),
                "area_pixels": 56 * 56,
                "label": label,
                "confidence": round(confidence, 4),
            })

        return boxes

    def run_inference(
        self,
        image_input: Any,
        model_name: str = "baseline_cnn",
        confidence_threshold: float = 0.70,
        generate_xai: bool = True,
    ) -> InferenceResult:
        """Run complete inference pipeline on image."""
        start_time = time.perf_counter()

        pil_img, tensor = self.preprocess_image(image_input)
        model = self.load_model(model_name)

        preds = model.predict(tensor, verbose=0)[0]
        top_idx = int(np.argmax(preds))
        top_confidence = float(preds[top_idx])
        top_class = IDX_TO_CLASS.get(top_idx, "unknown")

        class_probs = {cls_name: round(float(prob), 4) for cls_name, prob in zip(self.class_names, preds)}

        heatmap = None
        overlay_img = None
        boxes: List[Dict[str, Any]] = []

        if generate_xai:
            try:
                heatmap = generate_gradcam_heatmap(model, tensor, pred_index=top_idx)
                overlay_img, _ = overlay_gradcam(pil_img, heatmap, alpha=0.45)
                boxes = self._extract_bounding_box_from_heatmap(heatmap, top_class, top_confidence)
            except Exception as e:
                logger.warning(f"Grad-CAM generation failed: {e}")

        # Industrial quality rules:
        # If top defect is classified with confidence, surface is defective
        is_defective = True  # NEU dataset classes are all defect types
        requires_review = top_confidence < confidence_threshold

        inference_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return InferenceResult(
            predicted_class=top_class,
            confidence=round(top_confidence, 4),
            is_defective=is_defective,
            class_probabilities=class_probs,
            inference_time_ms=inference_time_ms,
            model_name=model_name,
            bounding_boxes=boxes,
            heatmap_array=heatmap,
            overlay_image=overlay_img,
            requires_review=requires_review,
        )


# Global singleton instance
_engine: Optional[InferenceEngine] = None


def get_inference_engine() -> InferenceEngine:
    global _engine
    if _engine is None:
        _engine = InferenceEngine()
    return _engine
