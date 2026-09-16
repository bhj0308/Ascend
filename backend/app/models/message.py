"""Message Model - In-app messaging between users."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Message(BaseModel):
    """In-app message model."""

    __tablename__ = "messages"

    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Optional context: which job this conversation relates to
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True, index=True)

    body = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)

    # Relationships
    sender = relationship(
        "User", back_populates="sent_messages", foreign_keys=[sender_id]
    )
    recipient = relationship(
        "User", back_populates="received_messages", foreign_keys=[recipient_id]
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id})>"
