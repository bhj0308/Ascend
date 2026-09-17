"""Contract request/response schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.contract import Contract, ContractStatus, ContractTemplateType


class ContractCreate(BaseModel):
    """Fields required to generate a contract from a template."""

    application_id: int
    template_type: ContractTemplateType
    terms: Dict[str, Any]


class ContractUpdate(BaseModel):
    """Fields for updating a draft contract's terms."""

    terms: Dict[str, Any]


class TemplateInfo(BaseModel):
    """Description of an available contract template."""

    type: ContractTemplateType
    label: str
    description: str
    required_terms: List[str]


class ContractResponse(BaseModel):
    """Public-facing contract representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: Optional[int] = None
    template_type: ContractTemplateType
    status: ContractStatus
    terms: Dict[str, Any]
    signed_at: Optional[datetime] = None
    created_at: datetime

    # Derived from contract.application.job, always populated via
    # build_contract_response() below.
    job_id: int
    job_title: str
    founder_id: int
    applicant_id: int


def build_contract_response(contract: Contract) -> ContractResponse:
    """Build a ContractResponse, deriving job/founder/applicant fields.

    Every route that returns a contract should go through this helper so
    the derived fields (which come from `contract.application.job`) are
    always populated consistently.
    """
    application = contract.application
    job = application.job
    return ContractResponse(
        id=contract.id,
        application_id=contract.application_id,
        template_type=contract.template_type,
        status=contract.status,
        terms=contract.terms,
        signed_at=contract.signed_at,
        created_at=contract.created_at,
        job_id=job.id,
        job_title=job.title,
        founder_id=job.creator_id,
        applicant_id=application.user_id,
    )
