import re
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import (
    get_password_hash,
    verify_password,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from backend.app.core.exceptions import (
    ConflictException,
    UnauthorizedException,
    NotFoundException,
    ForbiddenException,
)
from backend.app.models.user import User
from backend.app.models.organization import Organization
from backend.app.models.membership import OrganizationMembership, OrganizationRole
from backend.app.models.refresh_token import RefreshToken
from backend.app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    TokenResponse,
    UserProfileResponse,
    MembershipSummary,
)


class AuthService:
    """Authentication and tenant session management service."""

    def __init__(self, db: Session):
        self.db = db

    def _hash_token(self, token: str) -> str:
        """Hashes refresh token string using SHA256 before database persistence."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _generate_slug(self, name: str) -> str:
        """Generates a clean, unique URL slug for an organization."""
        base_slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
        if not base_slug:
            base_slug = "org"

        slug = base_slug
        counter = 1
        while self.db.query(Organization).filter(Organization.slug == slug).first() is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def _build_user_profile(self, user: User) -> UserProfileResponse:
        memberships_data = []
        for m in user.memberships:
            if m.is_active:
                memberships_data.append(
                    MembershipSummary(
                        id=m.id,
                        organization_id=m.organization.id,
                        organization_name=m.organization.name,
                        organization_slug=m.organization.slug,
                        role=m.role,
                        is_active=m.is_active,
                    )
                )

        return UserProfileResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_super_admin=user.is_super_admin,
            created_at=user.created_at,
            memberships=memberships_data,
        )

    def register(self, payload: UserRegisterRequest) -> AuthResponse:
        # Enforce password strength
        validate_password_strength(payload.password)

        normalized_email = payload.email.strip().lower()

        # Check existing user
        if self.db.query(User).filter(User.email == normalized_email).first() is not None:
            raise ConflictException("An account with this email address already exists.")

        try:
            # 1. Create User
            user = User(
                email=normalized_email,
                hashed_password=get_password_hash(payload.password),
                full_name=payload.full_name.strip(),
                is_active=True,
                is_super_admin=False,
                email_verified=False,
            )
            self.db.add(user)
            self.db.flush()

            # 2. Create Organization
            slug = self._generate_slug(payload.organization_name)
            org = Organization(
                name=payload.organization_name.strip(),
                slug=slug,
                industry=payload.industry,
                contact_email=normalized_email,
                is_active=True,
            )
            self.db.add(org)
            self.db.flush()

            # 3. Create Owner Membership
            membership = OrganizationMembership(
                user_id=user.id,
                organization_id=org.id,
                role=OrganizationRole.OWNER,
                is_active=True,
            )
            self.db.add(membership)
            self.db.flush()

            # 4. Issue Tokens
            claims = {"org_id": org.id, "role": OrganizationRole.OWNER.value}
            access_token = create_access_token(subject=user.id, custom_claims=claims)
            refresh_token = create_refresh_token(subject=user.id)

            # 5. Persist Refresh Token Record
            refresh_record = RefreshToken(
                user_id=user.id,
                token_hash=self._hash_token(refresh_token),
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                is_revoked=False,
            )
            self.db.add(refresh_record)

            self.db.commit()
            self.db.refresh(user)

            return AuthResponse(
                user=self._build_user_profile(user),
                tokens=TokenResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                ),
                active_organization_id=org.id,
            )

        except Exception as e:
            self.db.rollback()
            raise e

    def login(self, payload: UserLoginRequest) -> AuthResponse:
        normalized_email = payload.email.strip().lower()
        user = self.db.query(User).filter(User.email == normalized_email).first()

        if not user or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise ForbiddenException("Account is inactive. Please contact your organization administrator.")

        # Find primary active organization
        active_memberships = [m for m in user.memberships if m.is_active]
        if not active_memberships:
            raise ForbiddenException("Account is not affiliated with any active organization.")

        primary_membership = active_memberships[0]
        claims = {
            "org_id": primary_membership.organization_id,
            "role": primary_membership.role.value,
        }

        access_token = create_access_token(subject=user.id, custom_claims=claims)
        refresh_token = create_refresh_token(subject=user.id)

        # Store refresh token record
        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=self._hash_token(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            is_revoked=False,
        )
        self.db.add(refresh_record)
        self.db.commit()
        self.db.refresh(user)

        return AuthResponse(
            user=self._build_user_profile(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            ),
            active_organization_id=primary_membership.organization_id,
        )

    def refresh(self, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type. Refresh token required.")

        user_id = payload.get("sub")
        token_hash = self._hash_token(refresh_token_str)

        # Verify against database record
        token_record = self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked.is_(False),
        ).first()

        if not token_record:
            raise UnauthorizedException("Refresh token is invalid or has been revoked.")

        now_utc = datetime.now(timezone.utc)
        if token_record.expires_at.replace(tzinfo=timezone.utc) < now_utc:
            token_record.is_revoked = True
            self.db.commit()
            raise UnauthorizedException("Refresh token has expired.")

        # Revoke old refresh token (Token Rotation)
        token_record.is_revoked = True

        # Issue new token pair
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise UnauthorizedException("User account invalid or deactivated.")

        active_memberships = [m for m in user.memberships if m.is_active]
        claims = {}
        if active_memberships:
            claims = {
                "org_id": active_memberships[0].organization_id,
                "role": active_memberships[0].role.value,
            }

        new_access_token = create_access_token(subject=user.id, custom_claims=claims)
        new_refresh_token = create_refresh_token(subject=user.id)

        new_record = RefreshToken(
            user_id=user.id,
            token_hash=self._hash_token(new_refresh_token),
            expires_at=now_utc + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            is_revoked=False,
        )
        self.db.add(new_record)
        self.db.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def logout(self, refresh_token_str: Optional[str]) -> bool:
        if refresh_token_str:
            token_hash = self._hash_token(refresh_token_str)
            token_record = self.db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
            if token_record:
                token_record.is_revoked = True
                self.db.commit()
        return True

    def get_user_profile(self, user: User) -> UserProfileResponse:
        return self._build_user_profile(user)

    def request_password_reset(self, email: str) -> str:
        from backend.app.services.email import EmailService

        user = self.db.query(User).filter(User.email == email.strip().lower()).first()
        if not user:
            return "Reset instructions dispatched if account exists."

        token = EmailService.send_password_reset_email(user.email)
        return token

    def reset_password(self, token: str, new_password: str) -> bool:
        from backend.app.services.email import EmailService

        email = EmailService.verify_signed_token(token, expected_purpose="password_reset")
        if not email:
            raise UnauthorizedException("Invalid or expired password reset token.")

        validate_password_strength(new_password)
        user = self.db.query(User).filter(User.email == email.lower()).first()
        if not user:
            raise NotFoundException("User not found.")

        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        return True

    def verify_email(self, token: str) -> bool:
        from backend.app.services.email import EmailService

        email = EmailService.verify_signed_token(token, expected_purpose="email_verification")
        if not email:
            raise UnauthorizedException("Invalid or expired email verification token.")

        user = self.db.query(User).filter(User.email == email.lower()).first()
        if not user:
            raise NotFoundException("User not found.")

        if hasattr(user, "is_verified"):
            setattr(user, "is_verified", True)
            self.db.commit()
        return True

