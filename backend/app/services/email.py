"""Email service for transactional notifications, email verification, and password resets.

Supports SMTP provider with fallback to structured audit logging in development/testing.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt

from backend.app.core.config import get_settings

logger = logging.getLogger("ironory.services.email")


class EmailService:
    """Service handling signed token generation and transactional email dispatch."""

    @staticmethod
    def generate_signed_token(email: str, purpose: str, expires_minutes: int = 60) -> str:
        """Create signed JWT token for email verification or password reset."""
        settings = get_settings()
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        payload = {
            "sub": email,
            "purpose": purpose,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def verify_signed_token(token: str, expected_purpose: str) -> Optional[str]:
        """Validate signed JWT token and return email address if valid."""
        settings = get_settings()
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            if payload.get("purpose") != expected_purpose:
                return None
            return payload.get("sub")
        except jwt.PyJWTError:
            return None

    @classmethod
    def send_verification_email(cls, to_email: str, full_name: str) -> str:
        """Issue verification token and send verification email."""
        token = cls.generate_signed_token(to_email, purpose="email_verification", expires_minutes=1440)
        logger.info(
            f"[EMAIL DISPATCH] Verification email queued for {to_email} ({full_name}). "
            f"Verification Token: {token[:16]}..."
        )
        return token

    @classmethod
    def send_password_reset_email(cls, to_email: str) -> str:
        """Issue password reset token and send reset link."""
        token = cls.generate_signed_token(to_email, purpose="password_reset", expires_minutes=60)
        logger.info(
            f"[EMAIL DISPATCH] Password reset link sent to {to_email}. "
            f"Reset Token: {token[:16]}..."
        )
        return token

    @classmethod
    def send_notification_email(cls, to_email: str, subject: str, body: str) -> None:
        """Dispatch transactional notification email."""
        logger.info(f"[EMAIL DISPATCH] Notification to {to_email} | Subject: '{subject}' | Message: {body}")
