"""Application routes: apply to jobs, view applications, update status."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)

router = APIRouter()


@router.post("", response_model=ApplicationResponse, status_code=201)
def apply_to_job(
    payload: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply to a job posting."""
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = (
        db.query(Application)
        .filter(
            Application.job_id == payload.job_id, Application.user_id == current_user.id
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    application = Application(
        job_id=payload.job_id,
        user_id=current_user.id,
        cover_note=payload.cover_note,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/me", response_model=List[ApplicationResponse])
def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all applications submitted by the current user."""
    return (
        db.query(Application)
        .filter(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
        .all()
    )


@router.get("/job/{job_id}", response_model=List[ApplicationResponse])
def get_job_applications(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all applications for a job. Only the job creator can view."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.creator_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view these applications"
        )

    return db.query(Application).filter(Application.job_id == job_id).all()


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update application status. Only the related job's creator can update."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.job.creator_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this application"
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    return application
