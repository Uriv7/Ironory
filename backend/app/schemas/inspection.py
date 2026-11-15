from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from backend.app.models.inspection import InspectionStatus, ReviewDecision


class InspectionImageResponse(BaseModel):
    id: str
    storage_key: str
    original_filename: str
    file_size_bytes: int
    width: int
    height: int
    mime_type: str
    checksum_sha256: str


class DefectResponse(BaseModel):
    id: str
    defect_type: str
    severity: str
    bbox_x: Optional[float] = None
    bbox_y: Optional[float] = None
    bbox_w: Optional[float] = None
    bbox_h: Optional[float] = None
    confidence: Optional[float] = None


class InspectionResultResponse(BaseModel):
    id: str
    model_name: str
    model_version: str
    predicted_class: str
    confidence: float
    is_defective: bool
    anomaly_score: Optional[float] = None
    inference_time_ms: int
    created_at: datetime
    defects: List[DefectResponse] = []


class InspectionReviewResponse(BaseModel):
    id: str
    reviewer_id: Optional[str] = None
    decision: ReviewDecision
    final_class: str
    is_defective: bool
    notes: Optional[str] = None
    created_at: datetime


class InspectionResponse(BaseModel):
    id: str
    organization_id: str
    product_id: str
    inspector_id: Optional[str] = None
    status: InspectionStatus
    error_message: Optional[str] = None
    created_at: datetime
    image: Optional[InspectionImageResponse] = None
    result: Optional[InspectionResultResponse] = None
    review: Optional[InspectionReviewResponse] = None


class HumanReviewRequest(BaseModel):
    decision: ReviewDecision
    final_class: str = Field(..., min_length=2, max_length=100)
    is_defective: bool
    notes: Optional[str] = Field(None, max_length=1000)


class BatchInspectionResponse(BaseModel):
    batch_size: int
    successful_count: int
    failed_count: int
    inspections: List[InspectionResponse]

