import logging
import sys
from typing import Any, Dict
from backend.app.core.config import settings


class CorrelationFormatter(logging.Formatter):
    """Custom formatter including correlation ID and timestamp in log records."""

    def format(self, record: logging.LogRecord) -> str:
        from backend.app.middleware.correlation import correlation_id_ctx
        record.correlation_id = getattr(record, "correlation_id", None) or correlation_id_ctx.get()
        return super().format(record)


def configure_logging() -> None:
    """Configures structured application logging."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    log_format = (
        "[%(asctime)s] [%(levelname)s] [req:%(correlation_id)s] "
        "[%(name)s:%(lineno)d]: %(message)s"
    )

    formatter = CorrelationFormatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if reloaded
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
    else:
        root_logger.handlers = [console_handler]

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DATABASE_ECHO else logging.WARNING
    )
