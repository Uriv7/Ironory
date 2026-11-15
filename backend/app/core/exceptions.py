from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception for handled errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}


class NotFoundException(AppException):
    def __init__(self, message: str, code: str = "RESOURCE_NOT_FOUND", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, code, details)


class ConflictException(AppException):
    def __init__(self, message: str, code: str = "RESOURCE_CONFLICT", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_409_CONFLICT, code, details)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required", code: str = "UNAUTHORIZED", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, code, details)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Access forbidden", code: str = "FORBIDDEN", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, code, details)


class ValidationException(AppException):
    def __init__(self, message: str, code: str = "VALIDATION_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, code, details)


class DatabaseException(AppException):
    def __init__(self, message: str = "Database operation failed", code: str = "DATABASE_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, code, details)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", "-")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
            "correlation_id": correlation_id,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", "-")
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append({
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", ""),
            "type": error.get("type", ""),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": {"errors": formatted_errors},
            },
            "correlation_id": correlation_id,
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", "-")
    logger.exception(f"Unhandled system error [req:{correlation_id}]: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please contact support with the correlation ID.",
                "details": {},
            },
            "correlation_id": correlation_id,
        },
    )
