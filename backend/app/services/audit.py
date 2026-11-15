"""Audit service for logging security and compliance activities."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from backend.app.models.audit import AuditLog

logger = logging.getLogger("ironory.services.audit")


class AuditService:
    """Records audit logs within transactions."""

    @staticmethod
    def log(
        db: Session,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        org_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Create and commit an audit log record."""
        entry = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            organization_id=org_id,
            actor_id=actor_id,
            details=details or {},
            ip_address=ip_address,
        )
        db.add(entry)
        try:
            db.commit()
            db.refresh(entry)
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to record audit log: {e}")
        return entry

    @staticmethod
    def get_tenant_logs(
        db: Session,
        org_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Retrieve paginated audit logs for a specific tenant organization."""
        return (
            db.query(AuditLog)
            .filter(AuditLog.organization_id == org_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
