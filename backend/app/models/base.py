"""Base model for all SQLAlchemy models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common fields for all models.

    Includes:
    - id: Primary key
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last updated
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
