from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class InspectionConfigSchema(BaseModel):
    model_type: str = Field("BASELINE_CNN", description="AI model architecture")
    confidence_threshold: float = Field(0.75, ge=0.0, le=1.0)
    anomaly_threshold: float = Field(0.05, ge=0.0, le=1.0)
    defect_classes: List[str] = Field(
        default=["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]
    )


class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    sku: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field("Steel Surface", max_length=100)
    configuration: Optional[InspectionConfigSchema] = None


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    sku: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    configuration: Optional[InspectionConfigSchema] = None


class ProductResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    sku: str
    code: str
    description: Optional[str] = None
    category: str
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    configuration: Optional[InspectionConfigSchema] = None
