from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.organization import Organization
from backend.app.models.membership import OrganizationMembership, OrganizationRole
from backend.app.security.tenant import get_current_tenant, get_current_tenant_membership
from backend.app.security.rbac import require_roles
from backend.app.repositories.product_repository import ProductRepository
from backend.app.core.exceptions import NotFoundException
from backend.app.schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    InspectionConfigSchema,
)

router = APIRouter(prefix="/products", tags=["Product Catalog & Inspection Configurations"])


def _to_product_response(product) -> ProductResponse:
    config_schema = None
    if product.configuration:
        config_schema = InspectionConfigSchema(
            model_type=product.configuration.model_type,
            confidence_threshold=product.configuration.confidence_threshold,
            anomaly_threshold=product.configuration.anomaly_threshold,
            defect_classes=product.configuration.defect_classes,
        )

    return ProductResponse(
        id=product.id,
        organization_id=product.organization_id,
        name=product.name,
        sku=product.sku,
        code=product.code,
        description=product.description,
        category=product.category,
        image_url=product.image_url,
        is_active=product.is_active,
        created_at=product.created_at,
        configuration=config_schema,
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New Manufacturing Product",
    description="Registers a manufactured product or surface part with custom AI defect inspection thresholds."
)
def create_product(
    payload: ProductCreateRequest,
    current_org: Organization = Depends(get_current_tenant),
    membership: OrganizationMembership = Depends(require_roles([OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.QUALITY_MANAGER])),
    db: Session = Depends(get_db),
) -> ProductResponse:
    repo = ProductRepository(db)
    product = repo.create_product(current_org.id, payload)
    return _to_product_response(product)


@router.get(
    "",
    response_model=List[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="List Organization Products",
    description="Returns all registered products and parts belonging to the active tenant with optional filtering."
)
def list_products(
    query: Optional[str] = Query(None, description="Search by name, SKU, or product code"),
    category: Optional[str] = Query(None, description="Filter by surface defect category"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> List[ProductResponse]:
    repo = ProductRepository(db)
    products = repo.list_products(
        org_id=current_org.id,
        query=query,
        category=category,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )
    return [_to_product_response(p) for p in products]


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Product Details",
    description="Fetches product specification, SKU, and active inspection configuration rules."
)
def get_product(
    product_id: str,
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> ProductResponse:
    repo = ProductRepository(db)
    product = repo.get_by_id_and_org(product_id, current_org.id)
    if not product:
        raise NotFoundException(f"Product '{product_id}' not found in your organization.")
    return _to_product_response(product)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Product & AI Configuration",
    description="Modifies product parameters or AI model detection thresholds. Requires Admin or Quality Manager."
)
def update_product(
    product_id: str,
    payload: ProductUpdateRequest,
    current_org: Organization = Depends(get_current_tenant),
    membership: OrganizationMembership = Depends(require_roles([OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.QUALITY_MANAGER])),
    db: Session = Depends(get_db),
) -> ProductResponse:
    repo = ProductRepository(db)
    product = repo.get_by_id_and_org(product_id, current_org.id)
    if not product:
        raise NotFoundException(f"Product '{product_id}' not found in your organization.")

    updated = repo.update_product(product, payload)
    return _to_product_response(updated)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Archive Product",
    description="Soft-deletes a product to prevent new inspection sessions while preserving historical inspection audit trails."
)
def delete_product(
    product_id: str,
    current_org: Organization = Depends(get_current_tenant),
    membership: OrganizationMembership = Depends(require_roles([OrganizationRole.OWNER, OrganizationRole.ADMIN])),
    db: Session = Depends(get_db),
):
    repo = ProductRepository(db)
    product = repo.get_by_id_and_org(product_id, current_org.id)
    if not product:
        raise NotFoundException(f"Product '{product_id}' not found in your organization.")

    repo.delete_product(product)
    return {"message": f"Product '{product.name}' archived successfully."}
