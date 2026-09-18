"""Authentication routes: signup, login, token refresh, password reset,
email verification."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserStatus
from app.schemas.auth import (
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.schemas.user import (
    RefreshRequest,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth import (
    create_access_token,
    create_email_verify_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    password_fingerprint,
    verify_password,
)
from app.services.email import EmailMessage, get_email_sender
from app.services.ratelimit import limiter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
def signup(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with email/password."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        user_type=payload.user_type,
        country=payload.country,
        city=payload.city,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Best-effort: signup must never fail because the verification email did.
    try:
        settings = get_settings()
        token = create_email_verify_token(user.id)
        get_email_sender().send(
            EmailMessage(
                to=user.email,
                subject="Verify your Ascend email",
                text=f"Verify your email: {settings.APP_BASE_URL}/verify-email?token={token}",
            )
        )
    except Exception:
        logger.exception("Failed to send verification email to %s", user.email)

    return user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email/password and receive JWT tokens."""
    user = db.query(User).filter(User.email == payload.email).first()
    if (
        not user
        or not user.password_hash
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(status_code=403, detail="This account has been suspended")
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user."""
    return current_user


@router.post("/refresh", response_model=Token)
@limiter.limit("30/minute")
def refresh(request: Request, payload: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access + refresh token pair.

    Tokens are stateless: there is no server-side revocation list yet, so a
    refresh token stays valid until it expires (REFRESH_TOKEN_EXPIRE_DAYS).
    """
    data = decode_token(payload.refresh_token)
    if data is None or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    try:
        user_id = int(data.get("sub"))
    except (TypeError, ValueError):
        user_id = None
    user = db.query(User).filter(User.id == user_id).first() if user_id else None
    if user is None or user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("3/minute")
def forgot_password(
    request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)
):
    """Always returns the same generic message — never reveals whether the
    email is registered."""
    user = db.query(User).filter(User.email == payload.email).first()
    if user and user.password_hash:
        settings = get_settings()
        token = create_password_reset_token(user)
        get_email_sender().send(
            EmailMessage(
                to=user.email,
                subject="Reset your Ascend password",
                text=f"Reset your password: {settings.APP_BASE_URL}/reset-password?token={token}",
            )
        )
    return MessageResponse(detail="If that email exists, we sent a reset link.")


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit("5/minute")
def reset_password(
    request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)
):
    """Consume a password reset token and set a new password."""
    invalid = HTTPException(status_code=400, detail="Invalid or expired reset link")

    data = decode_token(payload.token)
    if data is None or data.get("type") != "password_reset":
        raise invalid

    try:
        user_id = int(data.get("sub"))
    except (TypeError, ValueError):
        raise invalid

    user = db.query(User).filter(User.id == user_id).first()
    if (
        user is None
        or user.status != UserStatus.ACTIVE
        or data.get("pwd") != password_fingerprint(user.password_hash)
    ):
        raise invalid

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return MessageResponse(detail="Password updated")


@router.post("/send-verification", response_model=MessageResponse)
@limiter.limit("3/minute")
def send_verification(request: Request, current_user: User = Depends(get_current_user)):
    """Send (or resend) the current user's email verification link."""
    if current_user.email_verified:
        return MessageResponse(detail="Already verified")

    settings = get_settings()
    token = create_email_verify_token(current_user.id)
    get_email_sender().send(
        EmailMessage(
            to=current_user.email,
            subject="Verify your Ascend email",
            text=f"Verify your email: {settings.APP_BASE_URL}/verify-email?token={token}",
        )
    )
    return MessageResponse(detail="Verification email sent")


@router.post("/verify-email", response_model=MessageResponse)
@limiter.limit("10/minute")
def verify_email(
    request: Request, payload: VerifyEmailRequest, db: Session = Depends(get_db)
):
    """Consume an email verification token.

    Idempotent: verifying an already-verified account with a still-valid
    token returns 200 again rather than an error.
    """
    invalid = HTTPException(
        status_code=400, detail="Invalid or expired verification link"
    )

    data = decode_token(payload.token)
    if data is None or data.get("type") != "verify_email":
        raise invalid

    try:
        user_id = int(data.get("sub"))
    except (TypeError, ValueError):
        raise invalid

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or user.status != UserStatus.ACTIVE:
        raise invalid

    user.email_verified = True
    db.commit()
    return MessageResponse(detail="Email verified")
