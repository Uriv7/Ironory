from typing import List, Callable
from fastapi import Depends
from backend.app.models.membership import OrganizationRole
from backend.app.core.exceptions import ForbiddenException

# Role hierarchy: higher roles inherit capabilities of lower roles
ROLE_HIERARCHY = {
    OrganizationRole.OWNER: 5,
    OrganizationRole.ADMIN: 4,
    OrganizationRole.QUALITY_MANAGER: 3,
    OrganizationRole.INSPECTOR: 2,
    OrganizationRole.READ_ONLY: 1,
}


def is_role_sufficient(user_role: OrganizationRole, required_role: OrganizationRole) -> bool:
    """Returns True if user_role level is greater than or equal to required_role."""
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)


def require_roles(allowed_roles: List[OrganizationRole]) -> Callable:
    """FastAPI dependency factory enforcing that the tenant user has one of the allowed roles."""
    from backend.app.security.tenant import get_current_tenant_membership
    from backend.app.models.membership import OrganizationMembership

    def role_checker(membership: OrganizationMembership = Depends(get_current_tenant_membership)) -> OrganizationMembership:
        if membership.role not in allowed_roles:
            # Check if user has a higher role that implicitly covers it
            if not any(is_role_sufficient(membership.role, allowed) for allowed in allowed_roles):
                raise ForbiddenException(
                    message=f"Action requires one of {[r.value for r in allowed_roles]} role permissions."
                )
        return membership

    return role_checker
