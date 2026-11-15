from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.organization import Organization
from backend.app.models.membership import OrganizationMembership, OrganizationRole
from backend.app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Repository handling persistence operations for Organizations and Memberships."""

    def __init__(self, db: Session):
        super().__init__(Organization, db)

    def get_by_slug(self, slug: str) -> Optional[Organization]:
        return self.db.query(Organization).filter(Organization.slug == slug.strip().lower()).first()

    def create_organization(
        self,
        name: str,
        slug: str,
        industry: Optional[str] = None,
        contact_email: Optional[str] = None,
        logo_url: Optional[str] = None
    ) -> Organization:
        org = Organization(
            name=name.strip(),
            slug=slug.strip().lower(),
            industry=industry,
            contact_email=contact_email.strip().lower() if contact_email else None,
            logo_url=logo_url
        )
        return self.create(org)

    def add_member(
        self,
        user_id: str,
        organization_id: str,
        role: OrganizationRole = OrganizationRole.INSPECTOR
    ) -> OrganizationMembership:
        membership = OrganizationMembership(
            user_id=user_id,
            organization_id=organization_id,
            role=role,
            is_active=True
        )
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def get_memberships_for_user(self, user_id: str) -> List[OrganizationMembership]:
        return self.db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.is_active.is_(True)
        ).all()
