"""Mentorship routes: request, and the accept/decline/complete lifecycle."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.mentorship import Mentorship, MentorshipStatus
from app.models.user import User
from app.schemas.mentorship import (
    MentorshipCreate,
    MentorshipResponse,
    build_mentorship_response,
)

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


@router.post("", response_model=MentorshipResponse, status_code=201)
def create_mentorship(
    payload: MentorshipCreate,
    current_user: User = Depends(get_current_user),
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
