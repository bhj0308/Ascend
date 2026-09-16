"""Contract request/response schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict

from app.models.contract import ContractStatus, ContractTemplateType


class ContractCreate(BaseModel):
    """Fields required to generate a contract from a template."""

    application_id: Optional[int] = None
    template_type: ContractTemplateType
    terms: Dict[str, Any]


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
