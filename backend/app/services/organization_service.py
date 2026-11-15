import uuid
import secrets
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    NotFoundException,
    ConflictException,
    ForbiddenException,
    ValidationException,
)
from backend.app.models.user import User
from backend.app.models.organization import Organization
from backend.app.models.membership import OrganizationMembership, OrganizationRole
from backend.app.models.invitation import Invitation
from backend.app.schemas.organization import (
    OrganizationResponse,
    OrganizationUpdateRequest,
    MemberResponse,
    InviteMemberRequest,
    UpdateMemberRoleRequest,
)


class OrganizationService:
    """Manages tenant profiles, memberships, invitations, and role assignments."""

    def __init__(self, db: Session):
        self.db = db

    def get_organization_profile(self, org: Organization) -> OrganizationResponse:
        return OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            industry=org.industry,
            contact_email=org.contact_email,
            logo_url=org.logo_url,
            is_active=org.is_active,
            created_at=org.created_at,
        )

    def update_organization_profile(self, org: Organization, payload: OrganizationUpdateRequest) -> OrganizationResponse:
        if payload.name:
            org.name = payload.name.strip()
        if payload.industry is not None:
            org.industry = payload.industry.strip() if payload.industry else None
        if payload.contact_email is not None:
            org.contact_email = payload.contact_email.strip().lower() if payload.contact_email else None
        if payload.logo_url is not None:
            org.logo_url = payload.logo_url.strip() if payload.logo_url else None

        self.db.commit()
        self.db.refresh(org)
        return self.get_organization_profile(org)

    def list_members(self, org_id: str) -> List[MemberResponse]:
        memberships = (
            self.db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.organization_id == org_id,
                OrganizationMembership.is_active.is_(True),
            )
            .all()
        )

        return [
            MemberResponse(
                id=m.id,
                user_id=m.user.id,
                email=m.user.email,
                full_name=m.user.full_name,
                role=m.role,
                is_active=m.is_active,
                created_at=m.created_at,
            )
            for m in memberships
        ]

    def invite_member(self, org_id: str, inviter_id: str, payload: InviteMemberRequest) -> MemberResponse:
        normalized_email = payload.email.strip().lower()

        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == normalized_email).first()

        if existing_user:
            # Check if already a member
            existing_membership = (
                self.db.query(OrganizationMembership)
                .filter(
                    OrganizationMembership.organization_id == org_id,
                    OrganizationMembership.user_id == existing_user.id,
                )
                .first()
            )
            if existing_membership and existing_membership.is_active:
                raise ConflictException("User is already an active member of this organization.")

            if existing_membership and not existing_membership.is_active:
                # Reactivate membership
                existing_membership.is_active = True
                existing_membership.role = payload.role
                self.db.commit()
                self.db.refresh(existing_membership)
                return MemberResponse(
                    id=existing_membership.id,
                    user_id=existing_user.id,
                    email=existing_user.email,
                    full_name=existing_user.full_name,
                    role=existing_membership.role,
                    is_active=True,
                    created_at=existing_membership.created_at,
                )

            # Create direct membership for existing registered user
            membership = OrganizationMembership(
                user_id=existing_user.id,
                organization_id=org_id,
                role=payload.role,
                is_active=True,
            )
            self.db.add(membership)
            self.db.commit()
            self.db.refresh(membership)
            return MemberResponse(
                id=membership.id,
                user_id=existing_user.id,
                email=existing_user.email,
                full_name=existing_user.full_name,
                role=membership.role,
                is_active=True,
                created_at=membership.created_at,
            )

        # For users who do not yet have an account, create an invitation record
        invitation_token = secrets.token_urlsafe(32)
        invitation = Invitation(
            organization_id=org_id,
            email=normalized_email,
            role=payload.role,
            token=invitation_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            invited_by_id=inviter_id,
        )
        self.db.add(invitation)
        self.db.commit()

        # Return a pending representation
        return MemberResponse(
            id=invitation.id,
            user_id="pending-invite",
            email=normalized_email,
            full_name=f"Invited ({normalized_email.split('@')[0]})",
            role=payload.role,
            is_active=False,
            created_at=invitation.created_at,
        )

    def update_member_role(self, org_id: str, target_user_id: str, payload: UpdateMemberRoleRequest) -> MemberResponse:
        membership = (
            self.db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.organization_id == org_id,
                OrganizationMembership.user_id == target_user_id,
                OrganizationMembership.is_active.is_(True),
            )
            .first()
        )
        if not membership:
            raise NotFoundException("Member not found in this organization.")

        # Prevent demoting the last Owner
        if membership.role == OrganizationRole.OWNER and payload.role != OrganizationRole.OWNER:
            owner_count = (
                self.db.query(OrganizationMembership)
                .filter(
                    OrganizationMembership.organization_id == org_id,
                    OrganizationMembership.role == OrganizationRole.OWNER,
                    OrganizationMembership.is_active.is_(True),
                )
                .count()
            )
            if owner_count <= 1:
                raise ForbiddenException("Cannot demote the sole owner of the organization.")

        membership.role = payload.role
        self.db.commit()
        self.db.refresh(membership)

        return MemberResponse(
            id=membership.id,
            user_id=membership.user.id,
            email=membership.user.email,
            full_name=membership.user.full_name,
            role=membership.role,
            is_active=membership.is_active,
            created_at=membership.created_at,
        )

    def remove_member(self, org_id: str, target_user_id: str) -> None:
        membership = (
            self.db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.organization_id == org_id,
                OrganizationMembership.user_id == target_user_id,
                OrganizationMembership.is_active.is_(True),
            )
            .first()
        )
        if not membership:
            raise NotFoundException("Member not found in this organization.")

        # Prevent removing the last Owner
        if membership.role == OrganizationRole.OWNER:
            owner_count = (
                self.db.query(OrganizationMembership)
                .filter(
                    OrganizationMembership.organization_id == org_id,
                    OrganizationMembership.role == OrganizationRole.OWNER,
                    OrganizationMembership.is_active.is_(True),
                )
                .count()
            )
            if owner_count <= 1:
                raise ForbiddenException("Cannot remove the sole owner of the organization.")

        membership.is_active = False
        self.db.commit()
