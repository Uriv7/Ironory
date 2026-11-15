from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from backend.app.models.membership import OrganizationRole


class UserRegisterRequest(BaseModel):
    """Payload for registering a new user along with their primary organization."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    organization_name: str = Field(..., min_length=2, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)


class UserLoginRequest(BaseModel):
    """Payload for user authentication."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Payload for rotating an expired access token using a valid refresh token."""
    refresh_token: str


class TokenResponse(BaseModel):
    """JWT Token credentials."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MembershipSummary(BaseModel):
    id: str
    organization_id: str
    organization_name: str
    organization_slug: str
    role: OrganizationRole
    is_active: bool


class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_super_admin: bool
    created_at: datetime
    memberships: List[MembershipSummary] = []


class AuthResponse(BaseModel):
    user: UserProfileResponse
    tokens: TokenResponse
    active_organization_id: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class VerifyEmailRequest(BaseModel):
    token: str

