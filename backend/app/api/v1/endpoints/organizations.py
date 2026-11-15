from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.organization import Organization
from backend.app.models.membership import OrganizationMembership, OrganizationRole
from backend.app.security.tenant import get_current_user, get_current_tenant_membership, get_current_tenant
from backend.app.security.rbac import require_roles
from backend.app.services.organization_service import OrganizationService
from backend.app.schemas.organization import (
    OrganizationResponse,
    OrganizationUpdateRequest,
    MemberResponse,
    InviteMemberRequest,
    UpdateMemberRoleRequest,
)

router = APIRouter(prefix="/organizations", tags=["Multi-Tenant Organizations"])


@router.get(
    "/current",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Active Organization",
    description="Retrieves profile and metadata for the current tenant organization."
)
def get_current_organization(
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db)
) -> OrganizationResponse:
    service = OrganizationService(db)
    return service.get_organization_profile(current_org)


@router.patch(
    "/current",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Organization Profile",
    description="Updates organization details. Requires OWNER or ADMIN role."
)
def update_current_organization(
    payload: OrganizationUpdateRequest,
    current_org: Organization = Depends(get_current_tenant),
    membership: OrganizationMembership = Depends(require_roles([OrganizationRole.OWNER, OrganizationRole.ADMIN])),
    db: Session = Depends(get_db)
) -> OrganizationResponse:
    service = OrganizationService(db)
    return service.update_organization_profile(current_org, payload)


@router.get(
    "/members",
    response_model=List[MemberResponse],
    status_code=status.HTTP_200_OK,
    summary="List Organization Members",
    description="Lists all team members and their assigned inspection/management roles within the current tenant."
)
def list_members(
    membership: OrganizationMembership = Depends(get_current_tenant_membership),
    db: Session = Depends(get_db)
) -> List[MemberResponse]:
    service = OrganizationService(db)
    return service.list_members(membership.organization_id)


@router.post(
    "/invitations",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite or Add Team Member",
    description="Adds an existing user or creates an invitation for a new employee. Requires OWNER or ADMIN role."
)
def invite_member(
    payload: InviteMemberRequest,
    membership: OrganizationMembership = Depends(require_roles([OrganizationRole.OWNER, OrganizationRole.ADMIN])),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MemberResponse:
    service = OrganizationService(db)
    return service.invite_member(membership.organization_id, current_user.id, payload)


@router.patch(
    "/members/{user_id}/role",
    response_model=MemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Change Member Role",
    description="Updates role of a team member. Requires OWNER or ADMIN role."
)
def update_member_role(
    user_id: str,
    payload: UpdateMemberRoleRequest,
    membership: OrganizationMembership = Depends(require_roles([OrganizationRole.OWNER, OrganizationRole.ADMIN])),
    db: Session = Depends(get_db)
) -> MemberResponse:
    service = OrganizationService(db)
    return service.update_member_role(membership.organization_id, user_id, payload)


@router.delete(
    "/members/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove Member",
    description="Deactivates a user's membership in the organization. Requires OWNER or ADMIN role."
)
def remove_member(
    user_id: str,
    membership: OrganizationMembership = Depends(require_roles([OrganizationRole.OWNER, OrganizationRole.ADMIN])),
    db: Session = Depends(get_db)
):
    service = OrganizationService(db)
    service.remove_member(membership.organization_id, user_id)
    return {"message": "Member removed successfully"}
