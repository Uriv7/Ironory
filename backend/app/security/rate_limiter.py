"""Sliding-window rate limiter for protecting authentication and API endpoints.

Prevents brute-force credential stuffing and API abuse.
Supports thread-safe in-memory sliding window with optional Redis backend adapter.
"""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Optional
from fastapi import HTTPException, Request, status

from backend.app.core.config import get_settings


class InMemoryRateLimiter:
    """Thread-safe sliding-window in-memory rate limiter."""

    def __init__(self):
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def is_rate_limited(self, key: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """Check if key has exceeded max_requests in sliding window_seconds."""
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            # Filter timestamps outside window
            valid_timestamps = [ts for ts in self._requests[key] if ts > window_start]
            if len(valid_timestamps) >= max_requests:
                return True

            valid_timestamps.append(now)
            self._requests[key] = valid_timestamps
            return False

    def reset(self, key: Optional[str] = None):
        """Reset rate limit history for a key or all keys."""
        with self._lock:
            if key:
                self._requests.pop(key, None)
            else:
                self._requests.clear()


_limiter = InMemoryRateLimiter()


def check_rate_limit(
    request: Request,
    max_requests: int = 15,
    window_seconds: int = 60,
    key_prefix: str = "ip",
):
    """FastAPI dependency to rate limit requests by client IP address."""
    settings = get_settings()
    if settings.environment == "test":
        return

    client_ip = request.client.host if request.client else "127.0.0.1"
    key = f"{key_prefix}:{client_ip}"

    if _limiter.is_rate_limited(key, max_requests=max_requests, window_seconds=window_seconds):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before submitting additional requests.",
        )
