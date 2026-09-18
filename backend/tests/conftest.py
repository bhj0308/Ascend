"""Shared pytest fixtures: test DB, test client, and auth helpers."""

import os

os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401  (registers all mapped classes on Base)
from app.database import get_db
from app.main import app
from app.models.base import Base
from app.models.user import User, UserType
from app.services.auth import create_email_verify_token

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://postgres@localhost:5433/ascend_test"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once for the test session, drop them afterward."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    # base_url="http://localhost" (rather than TestClient's default
    # "http://testserver") so the Host header passes the app's
    # TrustedHostMiddleware, which allows "localhost" but not "testserver".
    return TestClient(app, base_url="http://localhost")


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{time.time_ns()}@example.com"


def _signup_and_login(
    client: TestClient, user_type: str, verified: bool = True
) -> dict:
    email = _unique_email(user_type)
    password = "hunter22"
    signup_resp = client.post(
        "/api/auth/signup",
        json={
            "email": email,
            "password": password,
            "first_name": "Test",
            "last_name": user_type.title(),
            "user_type": user_type,
            "country": "CA",
        },
    )
    assert signup_resp.status_code == 201, signup_resp.text
    user_id = signup_resp.json()["id"]

    login_resp = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    assert login_resp.status_code == 200, login_resp.text
    token = login_resp.json()["access_token"]

    if verified:
        verify_resp = client.post(
            "/api/auth/verify-email",
            json={"token": create_email_verify_token(user_id)},
        )
        assert verify_resp.status_code == 200, verify_resp.text

    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": user_id,
        "email": email,
        "password": password,
    }


@pytest.fixture()
def founder(client):
    """A signed-up + logged-in founder: returns dict with headers and user_id."""
    return _signup_and_login(client, "founder")


@pytest.fixture()
def applicant(client):
    """A signed-up + logged-in engineer (applicant): returns dict with headers and user_id."""
    return _signup_and_login(client, "engineer")


@pytest.fixture()
def other_user(client):
    """A third, unrelated signed-up + logged-in user."""
    return _signup_and_login(client, "engineer")


@pytest.fixture()
def unverified_user(client):
    """A signed-up user who never clicked the verification link."""
    return _signup_and_login(client, "engineer", verified=False)


@pytest.fixture()
def admin(client):
    """An admin account, promoted in the DB — signup refuses user_type=admin."""
    data = _signup_and_login(client, "founder")
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.id == data["user_id"]).first()
        user.user_type = UserType.ADMIN
        db.commit()
    finally:
        db.close()
    return data
