"""Admin-only moderation endpoints.

Deliberately small: find a user or job, suspend or close it, undo a suspension.
Admin is never self-assigned (see schemas/user.py) — grant it with
scripts/make_admin.py.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_admin_user
from app.models.job import Job, JobStatus
from app.models.user import User, UserStatus
from app.schemas.job import JobResponse
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
def list_users(
    q: Optional[str] = Query(None, description="Match email, first or last name"),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """List users, newest first. Includes emails — this is the moderation view."""
    query = db.query(User)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                User.email.ilike(like),
                User.first_name.ilike(like),
                User.last_name.ilike(like),
            )
        )
    return query.order_by(User.created_at.desc()).limit(limit).all()


@router.post("/users/{user_id}/suspend", response_model=UserResponse)
def suspend_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Suspend an account and close its open jobs.

    A suspended user can't authenticate (get_current_user requires ACTIVE), so
    this stops them mid-session. Their records stay for counterparties.
    """
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot suspend yourself")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.status == UserStatus.INACTIVE:
        raise HTTPException(status_code=400, detail="Account is already deleted")

    user.status = UserStatus.SUSPENDED
    db.query(Job).filter(
        Job.creator_id == user.id, Job.status == JobStatus.OPEN
    ).update({"status": JobStatus.CLOSED})

    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/unsuspend", response_model=UserResponse)
def unsuspend_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Reactivate a suspended account. Jobs closed by the suspension stay closed."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.status != UserStatus.SUSPENDED:
        raise HTTPException(status_code=400, detail="Account is not suspended")

    user.status = UserStatus.ACTIVE
    db.commit()
    db.refresh(user)
    return user


@router.get("/jobs", response_model=List[JobResponse])
def list_jobs(
    q: Optional[str] = Query(None, description="Match title or company name"),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """List jobs in every status, newest first (browse only shows open ones)."""
    query = db.query(Job)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Job.title.ilike(like), Job.company_name.ilike(like)))
    return query.order_by(Job.created_at.desc()).limit(limit).all()


@router.post("/jobs/{job_id}/close", response_model=JobResponse)
def close_job(
    job_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Take a job off the board without deleting its applications."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == JobStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Job is already closed")

    job.status = JobStatus.CLOSED
    db.commit()
    db.refresh(job)
    return job
