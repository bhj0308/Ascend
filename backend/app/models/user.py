"""User Model - Users and their profiles."""

from enum import Enum

from sqlalchemy import JSON, Boolean, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class UserType(str, Enum):
    """User type enumeration."""

    FOUNDER = "founder"  # Hiring founder/CTO
    ENGINEER = "engineer"  # Tech professional
    IEC_WORKER = "iec_worker"  # IEC working holiday participant
    IMMIGRANT = "immigrant"  # Other immigrant/international talent
    ADMIN = "admin"


class UserStatus(str, Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(BaseModel):
    """User model for Ascend platform."""

    __tablename__ = "users"

    # Auth
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users

    # Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # Account
    user_type = Column(SQLEnum(UserType), nullable=False, index=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    # Location
    country = Column(String(2), nullable=True)  # ISO country code
    city = Column(String(100), nullable=True)

    # Contact
    phone = Column(String(20), nullable=True)

    # OAuth
    google_id = Column(String(255), nullable=True, unique=True)
    github_id = Column(String(255), nullable=True, unique=True)

    # Metadata
    skills = Column(JSON, nullable=True)  # Array of skills
    languages = Column(JSON, nullable=True)  # Array of languages
    timezone = Column(String(50), nullable=True)

    # Visa/Immigration Status
    visa_status = Column(String(100), nullable=True)  # e.g., "IEC", "PR", "Work Permit"
    visa_expiry = Column(String, nullable=True)  # ISO date string

    # Flags
    email_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)

    # Relationships
    created_jobs = relationship(
        "Job", back_populates="creator", foreign_keys="Job.creator_id"
    )
    applications = relationship(
        "Application", back_populates="user", foreign_keys="Application.user_id"
    )
    sent_messages = relationship(
        "Message", back_populates="sender", foreign_keys="Message.sender_id"
    )
    received_messages = relationship(
        "Message", back_populates="recipient", foreign_keys="Message.recipient_id"
    )
    mentorships_as_mentor = relationship(
        "Mentorship", back_populates="mentor", foreign_keys="Mentorship.mentor_id"
    )
    mentorships_as_mentee = relationship(
        "Mentorship", back_populates="mentee", foreign_keys="Mentorship.mentee_id"
    )
    sent_payments = relationship(
        "Payment", back_populates="from_user", foreign_keys="Payment.from_user_id"
    )
    received_payments = relationship(
        "Payment", back_populates="to_user", foreign_keys="Payment.to_user_id"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, type={self.user_type})>"
