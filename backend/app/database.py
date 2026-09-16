"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.base import Base

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=True,  # Verify connections before use
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency that yields a database session per-request
    and ensures it's closed afterward.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Used in development/testing; production uses Alembic migrations."""
    Base.metadata.create_all(bind=engine)
