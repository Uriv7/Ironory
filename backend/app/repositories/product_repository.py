from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.core.exceptions import ConflictException, NotFoundException
from backend.app.models.product import Product, InspectionConfiguration
from backend.app.schemas.product import ProductCreateRequest, ProductUpdateRequest


class ProductRepository:
    """Repository handling tenant-isolated persistence for manufactured products."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id_and_org(self, product_id: str, org_id: str) -> Optional[Product]:
        return (
            self.db.query(Product)
            .filter(Product.id == product_id, Product.organization_id == org_id)
            .first()
        )

    def get_by_code_and_org(self, code: str, org_id: str) -> Optional[Product]:
        return (
            self.db.query(Product)
            .filter(Product.code == code.strip(), Product.organization_id == org_id)
            .first()
        )

    def list_products(
        self,
        org_id: str,
        query: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Product]:
        stmt = self.db.query(Product).filter(Product.organization_id == org_id)

        if is_active is not None:
            stmt = stmt.filter(Product.is_active == is_active)

        if category:
            stmt = stmt.filter(Product.category == category.strip())

        if query:
            search = f"%{query.strip().lower()}%"
            stmt = stmt.filter(
                or_(
                    Product.name.ilike(search),
                    Product.sku.ilike(search),
                    Product.code.ilike(search),
                )
            )

        return stmt.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    def create_product(self, org_id: str, payload: ProductCreateRequest) -> Product:
        # Check uniqueness of product code within the organization
        existing = self.get_by_code_and_org(payload.code, org_id)
        if existing:
            raise ConflictException(f"A product with code '{payload.code}' already exists in your organization.")

        product = Product(
            organization_id=org_id,
            name=payload.name.strip(),
            sku=payload.sku.strip(),
            code=payload.code.strip(),
            description=payload.description.strip() if payload.description else None,
            category=payload.category.strip(),
            is_active=True,
        )
        self.db.add(product)
        self.db.flush()

        # Add inspection configuration
        config_data = payload.configuration
        config = InspectionConfiguration(
            product_id=product.id,
            model_type=config_data.model_type if config_data else "BASELINE_CNN",
            confidence_threshold=config_data.confidence_threshold if config_data else 0.75,
            anomaly_threshold=config_data.anomaly_threshold if config_data else 0.05,
            defect_classes=(
                config_data.defect_classes
                if config_data
                else ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]
            ),
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update_product(self, product: Product, payload: ProductUpdateRequest) -> Product:
        if payload.name is not None:
            product.name = payload.name.strip()
        if payload.sku is not None:
            product.sku = payload.sku.strip()
        if payload.description is not None:
            product.description = payload.description.strip() if payload.description else None
        if payload.category is not None:
            product.category = payload.category.strip()
        if payload.is_active is not None:
            product.is_active = payload.is_active

        if payload.configuration:
            if not product.configuration:
                product.configuration = InspectionConfiguration(product_id=product.id)
            product.configuration.model_type = payload.configuration.model_type
            product.configuration.confidence_threshold = payload.configuration.confidence_threshold
            product.configuration.anomaly_threshold = payload.configuration.anomaly_threshold
            product.configuration.defect_classes = payload.configuration.defect_classes

        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, product: Product) -> None:
        # Soft-delete by marking inactive to preserve historical inspection integrity
        product.is_active = False
        self.db.commit()
