"""Contract routes: templates, generation, and the send/sign/cancel lifecycle."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.application import Application
from app.models.contract import Contract, ContractStatus
from app.models.job import Job
from app.models.user import User
from app.schemas.contract import (
    ContractCreate,
    ContractResponse,
    ContractUpdate,
    TemplateInfo,
    build_contract_response,
)
from app.services.contracts import TEMPLATES, validate_term_types, validate_terms

router = APIRouter()


def _validate_terms_or_400(template_type, terms) -> None:
    """Raise 400 for missing required terms, then for wrong-typed values."""
    missing = validate_terms(template_type, terms)
    if missing:
        raise HTTPException(
            status_code=400, detail=f"Missing required terms: {', '.join(missing)}"
        )
    type_errors = validate_term_types(terms)
    if type_errors:
        raise HTTPException(status_code=400, detail="; ".join(type_errors))


@router.get("/templates", response_model=List[TemplateInfo])
def list_templates(current_user: User = Depends(get_current_user)):
    """List available contract templates and their required terms."""
    return [
        TemplateInfo(
            type=template_type,
            label=info["label"],
            description=info["description"],
            required_terms=info["required_terms"],
        )
        for template_type, info in TEMPLATES.items()
    ]


@router.get("/me", response_model=List[ContractResponse])
def get_my_contracts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List contracts where the current user is the job creator or the applicant."""
    contracts = (
        db.query(Contract)
        .join(Application, Contract.application_id == Application.id)
        .join(Job, Application.job_id == Job.id)
        .filter(
            or_(
                Job.creator_id == current_user.id,
                Application.user_id == current_user.id,
            )
        )
        .order_by(Contract.created_at.desc())
        .all()
    )
    return [build_contract_response(c) for c in contracts]


@router.post("", response_model=ContractResponse, status_code=201)
def create_contract(
    payload: ContractCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a draft contract from a template for an application.

    Only the job's creator (founder) may generate a contract, and only one
    contract may exist per application.
    """
    application = (
        db.query(Application).filter(Application.id == payload.application_id).first()
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.job.creator_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create a contract for this application",
        )

    existing = (
        db.query(Contract)
        .filter(Contract.application_id == payload.application_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Application already has a contract"
        )

    _validate_terms_or_400(payload.template_type, payload.terms)

    contract = Contract(
        application_id=payload.application_id,
        template_type=payload.template_type,
        terms=payload.terms,
        status=ContractStatus.DRAFT,
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return build_contract_response(contract)


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single contract. Only the founder or the applicant may view it."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if current_user.id not in (
        contract.application.job.creator_id,
        contract.application.user_id,
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to view this contract"
        )
    return build_contract_response(contract)


@router.put("/{contract_id}", response_model=ContractResponse)
def update_contract(
    contract_id: int,
    payload: ContractUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Replace a draft contract's terms. Founder only, draft status only."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract.application.job.creator_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this contract"
        )
    if contract.status != ContractStatus.DRAFT:
        raise HTTPException(
            status_code=400, detail="Only draft contracts can be updated"
        )

    _validate_terms_or_400(contract.template_type, payload.terms)

    contract.terms = payload.terms
    db.commit()
    db.refresh(contract)
    return build_contract_response(contract)


@router.post("/{contract_id}/send", response_model=ContractResponse)
def send_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a draft contract to the applicant for signature (DRAFT -> PENDING_SIGNATURE).

    Founder only. E-signature integration (DocuSign) is behind the
    `ENABLE_DOCUSIGN` feature flag and is not implemented here; while the
    flag is off, this is a manual status transition only — no external API
    call is made and no envelope is created.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract.application.job.creator_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to send this contract"
        )
    if contract.status != ContractStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft contracts can be sent")

    settings = get_settings()
    if settings.ENABLE_DOCUSIGN:
        # Not implemented: this would create a DocuSign envelope and store
        # its id on contract.docusign_envelope_id.
        pass

    contract.status = ContractStatus.PENDING_SIGNATURE
    db.commit()
    db.refresh(contract)
    return build_contract_response(contract)


@router.post("/{contract_id}/sign", response_model=ContractResponse)
def sign_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Applicant signs the contract (PENDING_SIGNATURE -> SIGNED).

    This records an in-app acknowledgment, not a legal e-signature. Only
    the application's applicant may sign; the founder cannot sign their own
    contract.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract.application.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to sign this contract"
        )
    if contract.status != ContractStatus.PENDING_SIGNATURE:
        raise HTTPException(
            status_code=400, detail="Only contracts pending signature can be signed"
        )

    contract.status = ContractStatus.SIGNED
    contract.signed_at = datetime.utcnow()
    db.commit()
    db.refresh(contract)
    return build_contract_response(contract)


@router.post("/{contract_id}/cancel", response_model=ContractResponse)
def cancel_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a contract. Founder only; signed contracts cannot be cancelled."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract.application.job.creator_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to cancel this contract"
        )
    if contract.status == ContractStatus.SIGNED:
        raise HTTPException(
            status_code=400, detail="Signed contracts cannot be cancelled"
        )

    contract.status = ContractStatus.CANCELLED
    db.commit()
    db.refresh(contract)
    return build_contract_response(contract)
