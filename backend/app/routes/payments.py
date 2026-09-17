"""Payment routes: creation and the pending/cancel/execute lifecycle.

Money does not move in this version. Execution is gated behind the
`ENABLE_WISE_PAYMENTS` feature flag and is not implemented; calling
`/execute` never changes a payment's status.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse, build_payment_response

router = APIRouter()


@router.get("/me", response_model=List[PaymentResponse])
def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List payments where the current user is the sender or the recipient."""
    payments = (
        db.query(Payment)
        .filter(
            or_(
                Payment.from_user_id == current_user.id,
                Payment.to_user_id == current_user.id,
            )
        )
        .order_by(Payment.created_at.desc())
        .all()
    )
    return [build_payment_response(p) for p in payments]


@router.post("", response_model=PaymentResponse, status_code=201)
def create_payment(
    payload: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a payment. The current user is always the sender.

    Exactly one of `to_user_id` (a platform user) or `recipient_email` (an
    external recipient) must be given. Money does not move here: the
    payment is created with status PENDING.
    """
    if bool(payload.to_user_id) == bool(payload.recipient_email):
        raise HTTPException(
            status_code=400,
            detail="Provide exactly one of to_user_id or recipient_email",
        )

    if payload.to_user_id is not None:
        if payload.to_user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot pay yourself")
        to_user = db.query(User).filter(User.id == payload.to_user_id).first()
        if not to_user:
            raise HTTPException(status_code=404, detail="Recipient user not found")

    payment = Payment(
        from_user_id=current_user.id,
        to_user_id=payload.to_user_id,
        amount=payload.amount,
        currency=payload.currency.upper(),
        payment_type=payload.payment_type,
        status=PaymentStatus.PENDING,
        recipient_name=payload.recipient_name,
        recipient_email=payload.recipient_email,
        notes=payload.notes,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return build_payment_response(payment)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single payment. Only the sender or the recipient may view it."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if current_user.id not in (payment.from_user_id, payment.to_user_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to view this payment"
        )
    return build_payment_response(payment)


@router.post("/{payment_id}/cancel", response_model=PaymentResponse)
def cancel_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a pending payment. Sender only; only pending payments can be cancelled."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.from_user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to cancel this payment"
        )
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=400, detail="Only pending payments can be cancelled"
        )

    payment.status = PaymentStatus.CANCELLED
    db.commit()
    db.refresh(payment)
    return build_payment_response(payment)


@router.post("/{payment_id}/execute")
def execute_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Execute a pending payment via Wise. Sender only; pending payments only.

    Not implemented in this version: money never moves and the payment's
    status is never changed by this endpoint, regardless of the
    `ENABLE_WISE_PAYMENTS` flag. It always responds 501.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.from_user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to execute this payment"
        )
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=400, detail="Only pending payments can be executed"
        )

    settings = get_settings()
    if not settings.ENABLE_WISE_PAYMENTS:
        raise HTTPException(
            status_code=501,
            detail="Payments are disabled: Wise integration is not enabled",
        )
    raise HTTPException(
        status_code=501, detail="Wise transfer execution is not implemented yet"
    )
