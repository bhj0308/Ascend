"""Mentorship routes: request, and the accept/decline/complete lifecycle."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_verified_user
from app.models.mentorship import Mentorship, MentorshipStatus
from app.models.user import User, UserStatus
from app.schemas.mentorship import (
    MentorshipCreate,
    MentorshipResponse,
    build_mentorship_response,
)
from app.schemas.user import PublicUserResponse

router = APIRouter()


@router.get("/me", response_model=List[MentorshipResponse])
def get_my_mentorships(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List mentorships where the current user is the mentor or the mentee."""
    mentorships = (
        db.query(Mentorship)
        .filter(
            or_(
                Mentorship.mentor_id == current_user.id,
                Mentorship.mentee_id == current_user.id,
            )
        )
        .order_by(Mentorship.created_at.desc())
        .all()
    )
    return [build_mentorship_response(m) for m in mentorships]


@router.get("/mentors", response_model=List[PublicUserResponse])
def list_mentors(
    skill: Optional[str] = None,
    country: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List available mentors, newest first, max 50. Excludes the caller.

    `skill` matches case-insensitively against any entry of the user's JSON
    `skills` array; `country` is an exact case-insensitive match. Both
    filters are applied in Python after the DB query -- fine at this scale
    (mentor pool is small); replace with SQL filtering if it grows.
    """
    mentors = (
        db.query(User)
        .filter(
            User.mentor_available == True,  # noqa: E712
            User.status == UserStatus.ACTIVE,
            User.id != current_user.id,
        )
        .order_by(User.created_at.desc())
        .all()
    )

    if skill:
        skill_lower = skill.lower()
        mentors = [
            mentor
            for mentor in mentors
            if mentor.skills and any(skill_lower in s.lower() for s in mentor.skills)
        ]

    if country:
        country_lower = country.lower()
        mentors = [
            mentor
            for mentor in mentors
            if mentor.country and mentor.country.lower() == country_lower
        ]

    return mentors[:50]


@router.post("", response_model=MentorshipResponse, status_code=201)
def create_mentorship(
    payload: MentorshipCreate,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    """Request a mentorship. The current user becomes the mentee.

    404 if the mentor doesn't exist, 400 if requesting yourself, and 400 if
    a mentorship between these two users (in either direction) already
    exists with status requested or active.
    """
    mentor = db.query(User).filter(User.id == payload.mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    if mentor.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=400, detail="This user's account is no longer active"
        )
    if payload.mentor_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Cannot request a mentorship with yourself"
        )

    existing = (
        db.query(Mentorship)
        .filter(
            or_(
                and_(
                    Mentorship.mentor_id == payload.mentor_id,
                    Mentorship.mentee_id == current_user.id,
                ),
                and_(
                    Mentorship.mentor_id == current_user.id,
                    Mentorship.mentee_id == payload.mentor_id,
                ),
            ),
            Mentorship.status.in_(
                [MentorshipStatus.REQUESTED, MentorshipStatus.ACTIVE]
            ),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="A mentorship between these users already exists"
        )

    mentorship = Mentorship(
        mentor_id=payload.mentor_id,
        mentee_id=current_user.id,
        notes=payload.notes,
        status=MentorshipStatus.REQUESTED,
    )
    db.add(mentorship)
    db.commit()
    db.refresh(mentorship)
    return build_mentorship_response(mentorship)


@router.get("/{mentorship_id}", response_model=MentorshipResponse)
def get_mentorship(
    mentorship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single mentorship. Only the mentor or the mentee may view it."""
    mentorship = db.query(Mentorship).filter(Mentorship.id == mentorship_id).first()
    if not mentorship:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    if current_user.id not in (mentorship.mentor_id, mentorship.mentee_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to view this mentorship"
        )
    return build_mentorship_response(mentorship)


@router.post("/{mentorship_id}/accept", response_model=MentorshipResponse)
def accept_mentorship(
    mentorship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept a requested mentorship (requested -> active). Mentor only."""
    mentorship = db.query(Mentorship).filter(Mentorship.id == mentorship_id).first()
    if not mentorship:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    if mentorship.mentor_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to accept this mentorship"
        )
    if mentorship.status != MentorshipStatus.REQUESTED:
        raise HTTPException(
            status_code=400, detail="Only requested mentorships can be accepted"
        )

    if mentorship.mentee.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=400, detail="The mentee's account is no longer active"
        )

    mentorship.status = MentorshipStatus.ACTIVE
    db.commit()
    db.refresh(mentorship)
    return build_mentorship_response(mentorship)


@router.post("/{mentorship_id}/decline", response_model=MentorshipResponse)
def decline_mentorship(
    mentorship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Decline a requested mentorship (requested -> declined). Mentor only."""
    mentorship = db.query(Mentorship).filter(Mentorship.id == mentorship_id).first()
    if not mentorship:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    if mentorship.mentor_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to decline this mentorship"
        )
    if mentorship.status != MentorshipStatus.REQUESTED:
        raise HTTPException(
            status_code=400, detail="Only requested mentorships can be declined"
        )

    mentorship.status = MentorshipStatus.DECLINED
    db.commit()
    db.refresh(mentorship)
    return build_mentorship_response(mentorship)


@router.post("/{mentorship_id}/complete", response_model=MentorshipResponse)
def complete_mentorship(
    mentorship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Complete an active mentorship (active -> completed). Mentor or mentee."""
    mentorship = db.query(Mentorship).filter(Mentorship.id == mentorship_id).first()
    if not mentorship:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    if current_user.id not in (mentorship.mentor_id, mentorship.mentee_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to complete this mentorship"
        )
    if mentorship.status != MentorshipStatus.ACTIVE:
        raise HTTPException(
            status_code=400, detail="Only active mentorships can be completed"
        )

    mentorship.status = MentorshipStatus.COMPLETED
    db.commit()
    db.refresh(mentorship)
    return build_mentorship_response(mentorship)
