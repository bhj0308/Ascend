"""Payment request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.payment import PaymentStatus, PaymentType


class PaymentCreate(BaseModel):
    """Fields required to initiate a payment."""

    to_user_id: Optional[int] = None
    amount: int  # In smallest currency unit (cents)
    currency: str
    payment_type: PaymentType
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
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
    created_at: datetime
