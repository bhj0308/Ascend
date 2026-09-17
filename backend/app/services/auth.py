"""Authentication service: password hashing and JWT token management."""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from app.config import get_settings
from app.models.user import User

settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create a short-lived JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """Create a long-lived JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token. Returns None if invalid/expired."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        return None


def password_fingerprint(password_hash: Optional[str]) -> str:
    """Short fingerprint of a password hash.

    Embedded in password reset tokens so they are single-use by construction:
    once the password changes, the fingerprint computed from the new hash no
    longer matches the one baked into an already-issued token.
    """
    return hashlib.sha256((password_hash or "").encode("utf-8")).hexdigest()[:16]


def create_password_reset_token(user: User) -> str:
    """Create a JWT for POST /auth/reset-password."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user.id),
        "type": "password_reset",
        "exp": expire,
        "pwd": password_fingerprint(user.password_hash),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_email_verify_token(user_id: int) -> str:
    """Create a JWT for POST /auth/verify-email."""
    expire = datetime.now(timezone.utc) + timedelta(
        hours=settings.EMAIL_VERIFY_EXPIRE_HOURS
    )
    payload = {"sub": str(user_id), "type": "verify_email", "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
