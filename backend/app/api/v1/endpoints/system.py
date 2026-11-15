from fastapi import APIRouter, status
from backend.app.core.config import settings
from backend.app.schemas.common import SystemInfoResponse

router = APIRouter(tags=["System"])


@router.get(
    "/system/info",
    response_model=SystemInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Public System Information",
    description="Returns public non-sensitive system metadata and capability flags."
)
def get_system_info() -> SystemInfoResponse:
    return SystemInfoResponse(
        app_name=settings.APP_NAME,
        version="1.0.0-foundation",
        api_prefix=settings.API_V1_PREFIX,
        environment=settings.ENVIRONMENT,
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        features={
            "multi_tenancy": True,
            "rbac": True,
            "async_inference": False,
            "academic_streamlit_demo": True,
        }
    )
