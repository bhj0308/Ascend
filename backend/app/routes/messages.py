"""Message routes: direct messaging between users, plain HTTP + polling.

No websockets. Clients are expected to poll `GET /threads` and
`GET /with/{user_id}` for updates.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.job import Job
from app.models.message import Message
from app.models.user import User
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    ThreadSummary,
)
from app.utils.names import display_name

router = APIRouter()


@router.post("", response_model=MessageResponse, status_code=201)
def send_message(
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message. The current user is always the sender.

    404 if the recipient doesn't exist or the optional `job_id` doesn't
    exist; 400 if sending to oneself or the body is empty/whitespace.
    """
    if payload.recipient_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send a message to yourself")

    recipient = db.query(User).filter(User.id == payload.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=400, detail="Message body cannot be empty")

    if payload.job_id is not None:
        job = db.query(Job).filter(Job.id == payload.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

    message = Message(
        sender_id=current_user.id,
        recipient_id=payload.recipient_id,
        job_id=payload.job_id,
        body=body,
        read=False,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/threads", response_model=List[ThreadSummary])
def get_threads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List one thread summary per user the current user has messaged with.

    MVP implementation: fetch every message involving the current user
    (ordered newest first) and de-duplicate by counterpart in Python. This
    is fine at MVP scale; if the message table grows large, replace this
    with a SQL query grouped by counterpart (e.g. a window function
    partitioned by counterpart id, or a per-counterpart subquery) instead
    of loading the full history into memory.
    """
    messages = (
        db.query(Message)
        .filter(
            or_(
                Message.sender_id == current_user.id,
                Message.recipient_id == current_user.id,
            )
        )
        .order_by(Message.created_at.desc())
        .all()
    )

    last_message_by_counterpart = {}
    unread_counts = {}
    for message in messages:
        if message.sender_id == current_user.id:
            counterpart_id = message.recipient_id
        else:
            counterpart_id = message.sender_id

        if counterpart_id not in last_message_by_counterpart:
            # First hit per counterpart is the most recent, since messages
            # are ordered newest first.
            last_message_by_counterpart[counterpart_id] = message

        if (
            message.recipient_id == current_user.id
            and message.sender_id == counterpart_id
            and not message.read
        ):
            unread_counts[counterpart_id] = unread_counts.get(counterpart_id, 0) + 1

    counterpart_ids = list(last_message_by_counterpart.keys())
    users_by_id = {
        user.id: user
        for user in db.query(User).filter(User.id.in_(counterpart_ids)).all()
    }

    threads = [
        ThreadSummary(
            user_id=counterpart_id,
            user_name=display_name(users_by_id[counterpart_id]),
            last_message_body=last_message.body,
            last_message_at=last_message.created_at,
            unread_count=unread_counts.get(counterpart_id, 0),
        )
        for counterpart_id, last_message in last_message_by_counterpart.items()
    ]
    threads.sort(key=lambda thread: thread.last_message_at, reverse=True)
    return threads


@router.get("/with/{user_id}", response_model=List[MessageResponse])
def get_thread_with_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the full message history with another user, oldest first.

    404 if that user doesn't exist. Any user may open a (possibly empty)
    thread with any existing user -- there is no 403 case here. As a side
    effect, every unread message that user sent to the current user is
    marked read.
    """
    other_user = db.query(User).filter(User.id == user_id).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")

    messages = (
        db.query(Message)
        .filter(
            or_(
                (Message.sender_id == current_user.id)
                & (Message.recipient_id == user_id),
                (Message.sender_id == user_id)
                & (Message.recipient_id == current_user.id),
            )
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    for message in messages:
        if (
            message.recipient_id == current_user.id
            and message.sender_id == user_id
            and not message.read
        ):
            message.read = True
    db.commit()

    return messages
