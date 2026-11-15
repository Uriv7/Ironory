from datetime import datetime, timezone
from fastapi import APIRouter, status, HTTPException
from backend.app.core.config import settings
from backend.app.db.session import check_db_connection
from backend.app.schemas.common import HealthResponse, ReadinessResponse

router = APIRouter(tags=["Health & Diagnostics"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Health Check",
    description="Returns HTTP 200 indicating that the backend process is running and alive."
)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc)
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Readiness Check",
    description="Verifies that all required system dependencies (database) are connected and ready."
)
def get_readiness() -> ReadinessResponse:
    db_ok = check_db_connection()
    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable"
        )
    return ReadinessResponse(
        status="ready",
        database="connected",
        timestamp=datetime.now(timezone.utc)
    )
