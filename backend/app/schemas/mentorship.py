"""Mentorship request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.mentorship import Mentorship, MentorshipStatus
from app.utils.names import display_name


class MentorshipCreate(BaseModel):
    """Fields required to request a mentorship."""

    mentor_id: int
    notes: Optional[str] = None


class MentorshipResponse(BaseModel):
    """Public-facing mentorship representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    mentor_id: int
    mentee_id: int
    status: MentorshipStatus
    notes: Optional[str] = None
    created_at: datetime

    # Derived from mentorship.mentor / mentorship.mentee, always populated
    # via build_mentorship_response() below.
    mentor_name: str
    mentee_name: str


def build_mentorship_response(mentorship: Mentorship) -> MentorshipResponse:
    """Build a MentorshipResponse, deriving mentor_name/mentee_name.

    Every route that returns a mentorship should go through this helper so
    the derived name fields are always populated consistently.
    """
    return MentorshipResponse(
        id=mentorship.id,
        mentor_id=mentorship.mentor_id,
        mentee_id=mentorship.mentee_id,
        status=mentorship.status,
        notes=mentorship.notes,
        created_at=mentorship.created_at,
        mentor_name=display_name(mentorship.mentor),
        mentee_name=display_name(mentorship.mentee),
    )
