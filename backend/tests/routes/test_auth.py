"""Tests for auth: server-side signup validation and the refresh-token flow."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from app.config import get_settings

PASSWORD = "testpass123"


def _signup(client, password=PASSWORD):
    email = f"auth-{uuid4().hex[:8]}@example.com"
    resp = client.post(
        "/api/auth/signup",
        json={"email": email, "password": password, "user_type": "engineer"},
    )
    return email, resp


def _login(client, email, password=PASSWORD):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_signup_rejects_short_password_server_side(client):
    _, resp = _signup(client, password="short7!")
    assert resp.status_code == 422, resp.text


def test_refresh_issues_working_tokens(client):
    email, resp = _signup(client)
    assert resp.status_code == 201, resp.text
    tokens = _login(client, email)

    refreshed = client.post(
        "/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refreshed.status_code == 200, refreshed.text
    new_tokens = refreshed.json()
    assert new_tokens["access_token"] and new_tokens["refresh_token"]

    me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["email"] == email


def test_refresh_rejects_access_token_and_garbage(client):
    email, _ = _signup(client)
    tokens = _login(client, email)

    # An access token is not a refresh token, even though it is a valid JWT.
    resp = client.post(
        "/api/auth/refresh", json={"refresh_token": tokens["access_token"]}
    )
    assert resp.status_code == 401, resp.text

    resp = client.post("/api/auth/refresh", json={"refresh_token": "not-a-jwt"})
    assert resp.status_code == 401, resp.text


def _signed(payload: dict) -> str:
    settings = get_settings()
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def test_refresh_rejects_signed_tokens_with_bad_or_missing_sub(client):
    exp = datetime.now(timezone.utc) + timedelta(minutes=5)
    for payload in (
        {"type": "refresh", "exp": exp},
        {"type": "refresh", "exp": exp, "sub": "abc"},
    ):
        resp = client.post(
            "/api/auth/refresh", json={"refresh_token": _signed(payload)}
        )
        assert resp.status_code == 401, resp.text


def test_access_token_with_non_numeric_sub_is_rejected_not_500(client):
    token = _signed(
        {
            "type": "access",
            "sub": "abc",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        }
    )
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401, resp.text
