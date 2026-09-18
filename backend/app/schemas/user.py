"""User request/response schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserStatus, UserType


class UserBase(BaseModel):
    """Shared user fields."""

    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: UserType
    country: Optional[str] = None
    city: Optional[str] = None


def _reject_self_assigned_admin(value: UserType) -> UserType:
    """Admin is granted out-of-band (scripts/make_admin.py), never by signing up."""
    if value == UserType.ADMIN:
        raise ValueError("user_type 'admin' cannot be self-assigned")
    return value


class UserCreate(UserBase):
    """Fields required to create a user via email/password signup."""

    password: str = Field(min_length=8)

    _no_admin = field_validator("user_type")(_reject_self_assigned_admin)


class UserCreateOAuth(UserBase):
    """Fields required to create a user via OAuth (Google)."""

    google_id: str
    avatar_url: Optional[str] = None

    _no_admin = field_validator("user_type")(_reject_self_assigned_admin)


class UserUpdate(BaseModel):
    """Fields a user can update on their own profile."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    timezone: Optional[str] = None
    visa_status: Optional[str] = None
    visa_expiry: Optional[str] = None
    mentor_available: Optional[bool] = None


class UserResponse(UserBase):
    """Public-facing user representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    visa_status: Optional[str] = None
    status: UserStatus
    email_verified: bool = False
    mentor_available: bool = False
    created_at: datetime


class PublicUserResponse(BaseModel):
    """What other signed-in users may see. Deliberately omits email and phone."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: UserType
    country: Optional[str] = None
    city: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    visa_status: Optional[str] = None
    status: UserStatus
    mentor_available: bool = False
    created_at: datetime


class UserLogin(BaseModel):
    """Login credentials."""

    email: EmailStr
    password: str


class DeleteAccountRequest(BaseModel):
    """Body for DELETE /profile/me."""

    password: str


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Body for POST /auth/refresh."""

    refresh_token: str
