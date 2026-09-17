"""Payment Model - Cross-border payments and remittances."""

from enum import Enum

from sqlalchemy import BigInteger, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class PaymentType(str, Enum):
    """Type of payment."""

    SALARY = "salary"
    CONTRACT_PAYMENT = "contract_payment"  # One-off contractor/gig payment
    REMITTANCE = "remittance"  # Personal money transfer (e.g., to family)


class PaymentStatus(str, Enum):
    """Payment processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Payment(BaseModel):
    """Cross-border payment/remittance model."""

    __tablename__ = "payments"

    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    to_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )  # Nullable: recipient may be external

    # Amount (stored as integer cents to avoid float rounding issues)
    amount = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False)  # ISO currency code, e.g. CAD, KRW

    payment_type = Column(SQLEnum(PaymentType), nullable=False)
    status = Column(
        SQLEnum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.PENDING,
        index=True,
    )

    # External provider tracking
    wise_transaction_id = Column(String(255), nullable=True)

    # Recipient details for external (non-platform-user) transfers
    recipient_name = Column(String(255), nullable=True)
    recipient_email = Column(String(255), nullable=True)

    notes = Column(String(500), nullable=True)

    # Relationships
    from_user = relationship(
        "User", back_populates="sent_payments", foreign_keys=[from_user_id]
    )
    to_user = relationship(
        "User", back_populates="received_payments", foreign_keys=[to_user_id]
    )

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, amount={self.amount} {self.currency}, status={self.status})>"
