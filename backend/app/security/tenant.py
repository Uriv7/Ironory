from typing import Optional
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.security import decode_token
from backend.app.core.exceptions import UnauthorizedException, ForbiddenException, NotFoundException
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.organization import Organization
from backend.app.models.membership import OrganizationMembership

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency extracting and authenticating the user from JWT Bearer token."""
    if not token:
        raise UnauthorizedException("Authentication token required.")

    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token missing subject identifier.")

    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user:
        raise UnauthorizedException("Authenticated user account no longer exists.")
    if not user.is_active:
        raise ForbiddenException("User account has been deactivated.")

    return user


def get_current_tenant_membership(
    user: User = Depends(get_current_user),
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID"),
    db: Session = Depends(get_db)
) -> OrganizationMembership:
    """
    FastAPI dependency enforcing tenant isolation.
    Validates that the authenticated user has an active membership in the requested organization.
    Cross-tenant requests from unauthorized organizations are rejected with HTTP 403 Forbidden.
    """
    query = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.is_active.is_(True)
    )

    if x_organization_id:
        membership = query.filter(OrganizationMembership.organization_id == x_organization_id.strip()).first()
        if not membership:
            raise ForbiddenException(
                message="Tenant isolation violation: You do not have access to this organization.",
                code="CROSS_TENANT_ACCESS_DENIED"
            )
        return membership

    # Default to user's first active membership if header is not explicitly set
    membership = query.first()
    if not membership:
        raise ForbiddenException(
            message="User does not have an active membership in any organization.",
            code="NO_TENANT_MEMBERSHIP"
        )
    return membership


def get_current_tenant(
    membership: OrganizationMembership = Depends(get_current_tenant_membership)
) -> Organization:
    """FastAPI dependency returning the validated active Organization entity."""
    return membership.organization
