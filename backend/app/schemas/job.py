"""Job request/response schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.job import JobStatus, JobType


class JobBase(BaseModel):
    """Shared job fields."""

    title: str
    description: str
    company_name: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "CAD"
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    job_type: JobType = JobType.FULL_TIME
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    remote_ok: bool = False
    visa_sponsorship: bool = False
    iec_friendly: bool = False
    positions_available: int = 1
    application_deadline: Optional[str] = None


class JobCreate(JobBase):
    """Fields required to create a job posting."""

    pass


class JobUpdate(BaseModel):
    """Fields that can be updated on a job posting."""

    title: Optional[str] = None
    description: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    skills: Optional[List[str]] = None
    status: Optional[JobStatus] = None
    positions_available: Optional[int] = None


class JobResponse(JobBase):
    """Public-facing job representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    creator_id: int
    status: JobStatus
    created_at: datetime


class JobFilters(BaseModel):
    """Query filters for browsing jobs."""

    skills: Optional[List[str]] = None
    location_country: Optional[str] = None
    remote_ok: Optional[bool] = None
    visa_sponsorship: Optional[bool] = None
    iec_friendly: Optional[bool] = None
    job_type: Optional[JobType] = None
    salary_min: Optional[int] = None
