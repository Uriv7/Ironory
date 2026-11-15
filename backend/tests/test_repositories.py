import pytest
from sqlalchemy.orm import Session
from backend.app.models.membership import OrganizationRole
from backend.app.repositories.user_repository import UserRepository
from backend.app.repositories.organization_repository import OrganizationRepository


def test_user_repository_crud(db_session: Session):
    user_repo = UserRepository(db_session)

    # Create user
    user = user_repo.create_user(
        email="Inspector1@Company.COM",
        hashed_password="hashed_secret_test_pw",
        full_name="Alex Inspector"
    )
    assert user.id is not None
    # Email should be normalized to lower case
    assert user.email == "inspector1@company.com"
    assert user.full_name == "Alex Inspector"
    assert user.is_active is True

    # Lookup by email
    found_user = user_repo.get_by_email("inspector1@company.com")
    assert found_user is not None
    assert found_user.id == user.id

    # Lookup non-existent
    assert user_repo.get_by_email("unknown@company.com") is None


def test_organization_and_membership_crud(db_session: Session):
    user_repo = UserRepository(db_session)
    org_repo = OrganizationRepository(db_session)

    # Create user
    user = user_repo.create_user(
        email="owner@acme-steel.com",
        hashed_password="hashed_secret_pw",
        full_name="Acme Owner"
    )

    # Create organization
    org = org_repo.create_organization(
        name="Acme Steel Corp",
        slug="acme-steel",
        industry="Metal & Steel Manufacturing",
        contact_email="contact@acme-steel.com"
    )
    assert org.id is not None
    assert org.slug == "acme-steel"
    assert org.industry == "Metal & Steel Manufacturing"

    # Add membership
    membership = org_repo.add_member(
        user_id=user.id,
        organization_id=org.id,
        role=OrganizationRole.OWNER
    )
    assert membership.id is not None
    assert membership.user_id == user.id
    assert membership.organization_id == org.id
    assert membership.role == OrganizationRole.OWNER

    # Query memberships for user
    memberships = org_repo.get_memberships_for_user(user.id)
    assert len(memberships) == 1
    assert memberships[0].organization.name == "Acme Steel Corp"
