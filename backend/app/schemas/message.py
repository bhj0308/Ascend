"""Message request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    """Fields required to send a message."""

    recipient_id: int
    body: str
    job_id: Optional[int] = None


class MessageResponse(BaseModel):
    """Public-facing message representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_id: int
    recipient_id: int
    job_id: Optional[int] = None
    body: str
    read: bool
    created_at: datetime


class ThreadSummary(BaseModel):
    """One row per counterpart a user has exchanged messages with."""

    user_id: int
    user_name: str
    last_message_body: str
    last_message_at: datetime
    unread_count: int
