"""Tests for rate limiting on /auth/*.

The rest of the suite runs with RATE_LIMIT_ENABLED=false (set in
tests/conftest.py) because it signs up dozens of users from one client IP,
which would otherwise trip these limits. This test re-enables the limiter
just for itself.
"""

from uuid import uuid4

import pytest

from app.services.ratelimit import limiter


@pytest.fixture()
def rate_limit_enabled():
    limiter.enabled = True
    limiter.reset()
    try:
        yield
    finally:
        limiter.enabled = False
        limiter.reset()


def test_login_returns_429_on_11th_attempt_within_a_minute(client, rate_limit_enabled):
    email = f"ratelimit-{uuid4().hex[:8]}@example.com"

    for _ in range(10):
        resp = client.post(
            "/api/auth/login", json={"email": email, "password": "wrong"}
        )
        assert resp.status_code == 401, resp.text

    resp = client.post("/api/auth/login", json={"email": email, "password": "wrong"})
    assert resp.status_code == 429, resp.text
    assert resp.json()["detail"] == "Too many requests. Try again in a minute."
