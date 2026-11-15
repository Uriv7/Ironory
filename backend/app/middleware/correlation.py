import uuid
import contextvars
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="-")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns or preserves a unique X-Correlation-ID header
    for end-to-end request tracing and structured logging.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = corr_id
        token = correlation_id_ctx.set(corr_id)

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = corr_id
            return response
        finally:
            correlation_id_ctx.reset(token)
