from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from backend.app.models.membership import OrganizationRole


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    industry: Optional[str] = None
    contact_email: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool
    created_at: datetime


class OrganizationUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    logo_url: Optional[str] = Field(None, max_length=512)


class MemberResponse(BaseModel):
    id: str
    user_id: str
    email: str
    full_name: str
    role: OrganizationRole
    is_active: bool
    created_at: datetime


class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: OrganizationRole = OrganizationRole.INSPECTOR


class UpdateMemberRoleRequest(BaseModel):
    role: OrganizationRole
