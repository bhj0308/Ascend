"""Application Model - User applications to job postings."""

from enum import Enum

from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ApplicationStatus(str, Enum):
    """Application status through the hiring pipeline."""

    APPLIED = "applied"
    REVIEWING = "reviewing"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    REJECTED = "rejected"
    HIRED = "hired"
    WITHDRAWN = "withdrawn"


class Application(BaseModel):
    """Job application model."""

    __tablename__ = "applications"

    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    status = Column(
        SQLEnum(ApplicationStatus),
        nullable=False,
        default=ApplicationStatus.APPLIED,
        index=True,
    )
    cover_note = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)  # Internal notes from hiring side

    # Relationships
    job = relationship("Job", back_populates="applications")
    user = relationship("User", back_populates="applications", foreign_keys=[user_id])
    contract = relationship("Contract", back_populates="application", uselist=False)

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, job_id={self.job_id}, user_id={self.user_id}, status={self.status})>"
