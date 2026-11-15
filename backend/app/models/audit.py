"""Platform & Inspection Audit Trail Model.

Captures immutable log entries for all compliance-relevant and administrative actions.
"""

from __future__ import annotations

from typing import Optional
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base, UUIDMixin, TimestampMixin


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """Immutable audit trail for ISO compliance and security tracking."""

    __tablename__ = "audit_logs"

    organization_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    actor_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
