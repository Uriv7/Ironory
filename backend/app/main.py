import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from backend.app.core.config import settings
from backend.app.core.logging import configure_logging
from backend.app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)
from backend.app.middleware.correlation import CorrelationIdMiddleware
from backend.app.api.v1.router import api_router

# Initialize structured logging
configure_logging()
logger = logging.getLogger(__name__)

# FastAPI Application Factory
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Industrial Quality Inspection SaaS Backend API",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# Correlation ID Middleware (must be outer-most to track all errors)
app.add_middleware(CorrelationIdMiddleware)

# Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)

# Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# API Routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
def root_status():
    """Root status endpoint confirming API gateway presence."""
    return {
        "service": settings.APP_NAME,
        "status": "online",
        "api_docs": f"{settings.API_V1_PREFIX}/docs"
    }


logger.info(f"{settings.APP_NAME} backend initialized successfully in {settings.ENVIRONMENT} mode.")
