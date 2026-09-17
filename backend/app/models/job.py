"""Job Model - Job postings from founders/companies."""

from enum import Enum

from sqlalchemy import JSON, BigInteger, Boolean, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class JobType(str, Enum):
    """Type of job posting."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class JobStatus(str, Enum):
    """Job posting status."""

    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    FILLED = "filled"


class Job(BaseModel):
    """Job posting model."""

    __tablename__ = "jobs"

    # Creator
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Basic Info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    company_name = Column(String(255), nullable=True)

    # Compensation
    salary_min = Column(BigInteger, nullable=True)  # In smallest currency unit (cents)
    salary_max = Column(BigInteger, nullable=True)
    salary_currency = Column(String(3), default="CAD")  # ISO currency code

    # Requirements
    skills = Column(JSON, nullable=True)  # Array of required skills
    experience_level = Column(
        String(50), nullable=True
    )  # e.g., "junior", "mid", "senior"

    # Type & Status
    job_type = Column(SQLEnum(JobType), nullable=False, default=JobType.FULL_TIME)
    status = Column(
        SQLEnum(JobStatus), nullable=False, default=JobStatus.OPEN, index=True
    )

    # Location
    location_country = Column(String(2), nullable=True)  # ISO country code
    location_city = Column(String(100), nullable=True)
    remote_ok = Column(Boolean, default=False)

    # Visa/Sponsorship
    visa_sponsorship = Column(Boolean, default=False)
    iec_friendly = Column(
        Boolean, default=False
    )  # Open to IEC working holiday participants

    # Metadata
    positions_available = Column(Integer, default=1)
    application_deadline = Column(String, nullable=True)  # ISO date string

    # Relationships
    creator = relationship(
        "User", back_populates="created_jobs", foreign_keys=[creator_id]
    )
    applications = relationship(
        "Application", back_populates="job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title={self.title}, status={self.status})>"
