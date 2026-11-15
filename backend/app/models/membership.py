import enum
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.organization import Organization


class OrganizationRole(str, enum.Enum):
    """Supported roles within a tenant organization."""
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    QUALITY_MANAGER = "QUALITY_MANAGER"
    INSPECTOR = "INSPECTOR"
    READ_ONLY = "READ_ONLY"


class OrganizationMembership(Base, UUIDMixin, TimestampMixin):
    """
    Connects a User to an Organization with a specific tenant role.
    Enforces that a user can have only one active membership per organization.
    """
    __tablename__ = "organization_memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_user_organization"),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[OrganizationRole] = mapped_column(
        Enum(OrganizationRole, name="org_role_enum", native_enum=False),
        nullable=False,
        default=OrganizationRole.INSPECTOR,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="memberships")
    organization: Mapped["Organization"] = relationship("Organization", back_populates="memberships")

    def __repr__(self) -> str:
        return f"<Membership user_id={self.user_id} org_id={self.organization_id} role={self.role}>"
