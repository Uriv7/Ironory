from typing import Optional, Generic, TypeVar, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    """Standardized API response envelope."""
    success: bool = True
    data: Optional[DataT] = None
    message: Optional[str] = None
    correlation_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    app_name: str
    environment: str
    timestamp: datetime


class ReadinessResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ready"})
    database: str = Field(..., json_schema_extra={"example": "connected"})
    timestamp: datetime


class SystemInfoResponse(BaseModel):
    app_name: str
    version: str
    api_prefix: str
    environment: str
    docs_url: str
    features: Dict[str, bool]
