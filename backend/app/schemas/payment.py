"""Payment request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import Payment, PaymentStatus, PaymentType
from app.utils.names import display_name


class PaymentCreate(BaseModel):
    """Fields required to initiate a payment."""

    to_user_id: Optional[int] = None
    recipient_email: Optional[str] = None
    recipient_name: Optional[str] = None
    amount: int = Field(gt=0)  # In smallest currency unit (cents)
    currency: str = Field(min_length=3, max_length=3)
    payment_type: PaymentType
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    """Public-facing payment representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    from_user_id: int
    to_user_id: Optional[int] = None
    amount: int
    currency: str
    payment_type: PaymentType
    status: PaymentStatus
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    # Derived from the from_user/to_user relationships, always populated via
    # build_payment_response() below.
    from_user_name: str
    to_user_name: Optional[str] = None


def build_payment_response(payment: Payment) -> PaymentResponse:
    """Build a PaymentResponse, deriving from_user_name/to_user_name.

    Every route that returns a payment should go through this helper so the
    derived name fields (which come from `payment.from_user`/`payment.to_user`)
    are always populated consistently.
    """
    return PaymentResponse(
        id=payment.id,
        from_user_id=payment.from_user_id,
        to_user_id=payment.to_user_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_type=payment.payment_type,
        status=payment.status,
        recipient_name=payment.recipient_name,
        recipient_email=payment.recipient_email,
        notes=payment.notes,
        created_at=payment.created_at,
        from_user_name=display_name(payment.from_user),
        to_user_name=display_name(payment.to_user) if payment.to_user else None,
    )
