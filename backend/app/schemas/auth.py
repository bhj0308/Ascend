"""Request/response schemas for password reset, email verification."""

from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    """Body for POST /auth/forgot-password."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Body for POST /auth/reset-password."""

    token: str
    new_password: str = Field(min_length=8)


class VerifyEmailRequest(BaseModel):
    """Body for POST /auth/verify-email."""

    token: str


class MessageResponse(BaseModel):
    """Generic `{"detail": "..."}` response used by the routes in this module."""

    detail: str
