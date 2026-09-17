"""Profile routes: view and update user profiles."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.job import Job, JobStatus
from app.models.user import User, UserStatus
from app.schemas.user import (
    DeleteAccountRequest,
    PublicUserResponse,
    UserResponse,
    UserUpdate,
)
from app.services.auth import verify_password

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's full profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's profile fields."""
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=204)
def delete_my_account(
    payload: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete (anonymize) the current user's account.

    We never hard-delete: counterparties keep their contract/payment/message
    records referencing this user's id. Instead we scrub personal fields,
    deactivate the account, close their open jobs, and clear the password
    so no one can log back in. 400 if the account has no password to check
    (e.g. OAuth-only); 401 if the password is wrong.
    """
    if not current_user.password_hash:
        raise HTTPException(
            status_code=400, detail="Contact support to delete this account"
        )
    if not verify_password(payload.password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")

    current_user.status = UserStatus.INACTIVE
    current_user.email = f"deleted-{current_user.id}@deleted.invalid"
    current_user.first_name = None
    current_user.last_name = None
    current_user.bio = None
    current_user.avatar_url = None
    current_user.phone = None
    current_user.city = None
    current_user.country = None
    current_user.skills = None
    current_user.languages = None
    current_user.visa_status = None
    current_user.timezone = None
    current_user.visa_expiry = None
    current_user.google_id = None
    current_user.github_id = None
    current_user.password_hash = None
    current_user.email_verified = False
    current_user.mentor_available = False

    db.query(Job).filter(
        Job.creator_id == current_user.id, Job.status == JobStatus.OPEN
    ).update({"status": JobStatus.CLOSED})

    db.commit()
    return None


@router.get("/{user_id}", response_model=PublicUserResponse)
def get_public_profile(user_id: int, db: Session = Depends(get_db)):
    """View another user's public profile (never includes their email)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
