from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, UUIDMixin, TimestampMixin
from backend.app.models.membership import OrganizationRole

if TYPE_CHECKING:
    from backend.app.models.organization import Organization
    from backend.app.models.user import User


class Invitation(Base, UUIDMixin, TimestampMixin):
    """
    Organization invitation entity for onboarding team members with assigned roles.
    """
    __tablename__ = "invitations"

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[OrganizationRole] = mapped_column(
        Enum(OrganizationRole, name="org_role_enum", native_enum=False),
        nullable=False,
        default=OrganizationRole.INSPECTOR
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    invited_by_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    invited_by: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return f"<Invitation email={self.email} org_id={self.organization_id} role={self.role}>"
