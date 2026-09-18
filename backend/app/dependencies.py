"""Shared FastAPI dependencies (auth guards, etc.)."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.user import User, UserStatus, UserType
from app.services.auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the current authenticated user from a JWT bearer token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
    except ValueError:
        raise credentials_exception
    if user is None:
        raise credentials_exception
    if user.status != UserStatus.ACTIVE:
        raise credentials_exception

    return user


def get_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """Require a verified email for actions that reach other users.

    Gated by REQUIRE_EMAIL_VERIFICATION: with no email provider configured the
    verification link only reaches the API log, so enforcing it would lock
    legitimate users out of the app entirely.
    """
    if get_settings().REQUIRE_EMAIL_VERIFICATION and not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verify your email address before doing this",
        )
    return current_user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Require an admin account. Granted only by scripts/make_admin.py."""
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user
