"""Contract Model - Employment agreements generated from templates."""

from enum import Enum

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ContractTemplateType(str, Enum):
    """Type of contract template used."""

    KOREA_ENGINEER_CANADA_CO = (
        "korea_engineer_canada_co"  # Korea-based engineer, Canadian company
    )
    CANADA_ENGINEER_KOREA_CO = (
        "canada_engineer_korea_co"  # Canada-based engineer, Korean company
    )
    REMOTE_CONTRACTOR = "remote_contractor"  # General remote contractor agreement
    FULL_TIME_DOMESTIC = "full_time_domestic"  # Standard same-country full-time
    PART_TIME_GIG = "part_time_gig"  # Part-time / gig work agreement


class ContractStatus(str, Enum):
    """Contract signature status."""

    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    SIGNED = "signed"
    CANCELLED = "cancelled"


class Contract(BaseModel):
    """Employment contract model."""

    __tablename__ = "contracts"

    application_id = Column(
        Integer, ForeignKey("applications.id"), nullable=True, index=True
    )

    template_type = Column(SQLEnum(ContractTemplateType), nullable=False)
    status = Column(
        SQLEnum(ContractStatus),
        nullable=False,
        default=ContractStatus.DRAFT,
        index=True,
    )

    # Contract terms (flexible JSON for different template needs)
    terms = Column(JSON, nullable=False)
    # Example terms structure:
    # {
    #   "salary": 80000, "currency": "CAD", "start_date": "2026-01-01",
    #   "end_date": null, "benefits": [...], "termination_clause": "...",
    #   "working_hours": "flexible", "reporting_country": "CA"
    # }

    # E-signature tracking
    docusign_envelope_id = Column(String(255), nullable=True)
    signed_at = Column(DateTime, nullable=True)

    # Relationships
    application = relationship("Application", back_populates="contract")

    def __repr__(self) -> str:
        return (
            f"<Contract(id={self.id}, type={self.template_type}, status={self.status})>"
        )
