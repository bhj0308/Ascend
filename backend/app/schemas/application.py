"""Application request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    """Fields required to apply to a job."""

    job_id: int
    cover_note: Optional[str] = None


class ApplicationUpdate(BaseModel):
    """Fields for updating an application (hiring side)."""

    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    """Public-facing application representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    user_id: int
    status: ApplicationStatus
    cover_note: Optional[str] = None
    created_at: datetime
