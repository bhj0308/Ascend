"""Job routes: post, browse, update, and delete job listings."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_verified_user
from app.models.job import Job, JobStatus
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse, JobUpdate

router = APIRouter()


@router.get("", response_model=List[JobResponse])
def browse_jobs(
    skills: Optional[List[str]] = Query(None),
    location_country: Optional[str] = None,
    remote_ok: Optional[bool] = None,
    visa_sponsorship: Optional[bool] = None,
    iec_friendly: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """Browse open job listings with optional filters."""
    query = db.query(Job).filter(Job.status == JobStatus.OPEN)

    if location_country:
        query = query.filter(Job.location_country == location_country)
    if remote_ok is not None:
        query = query.filter(Job.remote_ok == remote_ok)
    if visa_sponsorship is not None:
        query = query.filter(Job.visa_sponsorship == visa_sponsorship)
    if iec_friendly is not None:
        query = query.filter(Job.iec_friendly == iec_friendly)

    jobs = query.order_by(Job.created_at.desc()).all()

    # Skills filter applied in Python since it's a JSON array column
    if skills:
        jobs = [j for j in jobs if j.skills and any(s in j.skills for s in skills)]

    return jobs


@router.post("", response_model=JobResponse, status_code=201)
def create_job(
    payload: JobCreate,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    """Create a new job posting."""
    job = Job(creator_id=current_user.id, **payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a single job posting by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    payload: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a job posting. Only the creator can update."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this job")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a job posting. Only the creator can delete."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this job")

    db.delete(job)
    db.commit()
