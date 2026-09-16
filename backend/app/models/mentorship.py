"""Mentorship Model - Mentor-mentee relationships for IEC workers and newcomers."""

from enum import Enum

from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class MentorshipStatus(str, Enum):
    """Mentorship relationship status."""

    REQUESTED = "requested"
    ACTIVE = "active"
    COMPLETED = "completed"
    DECLINED = "declined"


class Mentorship(BaseModel):
    """Mentor-mentee relationship model."""

    __tablename__ = "mentorships"

    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mentee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    status = Column(
        SQLEnum(MentorshipStatus),
        nullable=False,
        default=MentorshipStatus.REQUESTED,
        index=True,
    )
    notes = Column(Text, nullable=True)

    # Relationships
    mentor = relationship(
        "User", back_populates="mentorships_as_mentor", foreign_keys=[mentor_id]
    )
    mentee = relationship(
        "User", back_populates="mentorships_as_mentee", foreign_keys=[mentee_id]
    )

    def __repr__(self) -> str:
        return f"<Mentorship(id={self.id}, mentor_id={self.mentor_id}, mentee_id={self.mentee_id}, status={self.status})>"
