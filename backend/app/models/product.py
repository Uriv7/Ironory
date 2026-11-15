from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Float, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.organization import Organization
    from backend.app.models.inspection import Inspection


class Product(Base, UUIDMixin, TimestampMixin):
    """
    Manufactured part or product catalog item registered for automated quality inspection.
    Enforces tenant-scoped unique product codes.
    """
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_organization_product_code"),
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="Steel Surface")
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    configuration: Mapped[Optional["InspectionConfiguration"]] = relationship(
        "InspectionConfiguration",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    inspections: Mapped[List["Inspection"]] = relationship(
        "Inspection",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} code={self.code} name={self.name}>"


class InspectionConfiguration(Base, UUIDMixin, TimestampMixin):
    """
    Product-specific deep learning inspection rules, thresholds, and accepted defect categories.
    """
    __tablename__ = "inspection_configurations"

    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    model_type: Mapped[str] = mapped_column(String(100), default="BASELINE_CNN", nullable=False)
    confidence_threshold: Mapped[float] = mapped_column(Float, default=0.75, nullable=False)
    anomaly_threshold: Mapped[float] = mapped_column(Float, default=0.05, nullable=False)
    defect_classes: Mapped[list] = mapped_column(
        JSON,
        default=lambda: ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"],
        nullable=False
    )

    # Relationship
    product: Mapped["Product"] = relationship("Product", back_populates="configuration")

    def __repr__(self) -> str:
        return f"<InspectionConfig product_id={self.product_id} model={self.model_type}>"
