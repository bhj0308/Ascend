"""Tests for auth: server-side signup validation, the refresh-token flow,
password reset, and email verification."""

import re
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from app.config import get_settings
from app.services.auth import create_email_verify_token, create_refresh_token
from app.services.email import RecordingEmailSender

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


def _use_recording_sender(monkeypatch) -> RecordingEmailSender:
    """Patch app.routes.auth.get_email_sender to hand back a fixed recorder."""
    sender = RecordingEmailSender()
    monkeypatch.setattr("app.routes.auth.get_email_sender", lambda: sender)
    return sender


def _extract_token(text: str, path: str) -> str:
    match = re.search(rf"{re.escape(path)}\?token=(\S+)", text)
    assert match, text
    return match.group(1)


def test_forgot_password_unknown_email_is_generic_and_sends_nothing(
    client, monkeypatch
):
    sender = _use_recording_sender(monkeypatch)
    resp = client.post(
        "/api/auth/forgot-password", json={"email": "nobody-here@example.com"}
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"detail": "If that email exists, we sent a reset link."}
    assert sender.sent == []


def test_forgot_password_reset_flow(client, monkeypatch):
    sender = _use_recording_sender(monkeypatch)
    email, resp = _signup(client)
    assert resp.status_code == 201, resp.text
    sender.sent.clear()  # drop the signup verification email

    resp = client.post("/api/auth/forgot-password", json={"email": email})
    assert resp.status_code == 200, resp.text
    assert len(sender.sent) == 1
    token = _extract_token(sender.sent[0].text, "/reset-password")

    new_password = "newpass456"
    reset_resp = client.post(
        "/api/auth/reset-password",
        json={"token": token, "new_password": new_password},
    )
    assert reset_resp.status_code == 200, reset_resp.text
    assert reset_resp.json() == {"detail": "Password updated"}

    ok = client.post("/api/auth/login", json={"email": email, "password": new_password})
    assert ok.status_code == 200, ok.text

    stale = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert stale.status_code == 401, stale.text

    # The same token cannot be reused: the fingerprint no longer matches.
    reused = client.post(
        "/api/auth/reset-password",
        json={"token": token, "new_password": "anotherpass789"},
    )
    assert reused.status_code == 400, reused.text


def test_reset_password_rejects_garbage_token(client):
    resp = client.post(
        "/api/auth/reset-password",
        json={"token": "not-a-jwt", "new_password": "newpass456"},
    )
    assert resp.status_code == 400, resp.text


def test_reset_password_rejects_short_password(client, monkeypatch):
    sender = _use_recording_sender(monkeypatch)
    email, _ = _signup(client)
    client.post("/api/auth/forgot-password", json={"email": email})
    token = _extract_token(sender.sent[-1].text, "/reset-password")

    resp = client.post(
        "/api/auth/reset-password", json={"token": token, "new_password": "short7"}
    )
    assert resp.status_code == 422, resp.text


def test_reset_password_rejects_wrong_token_type(client):
    email, _ = _signup(client)
    tokens = _login(client, email)
    resp = client.post(
        "/api/auth/reset-password",
        json={"token": tokens["access_token"], "new_password": "newpass456"},
    )
    assert resp.status_code == 400, resp.text


def test_signup_sends_one_verification_email(client, monkeypatch):
    sender = _use_recording_sender(monkeypatch)
    email, resp = _signup(client)
    assert resp.status_code == 201, resp.text
    assert len(sender.sent) == 1
    assert sender.sent[0].to == email
    _extract_token(sender.sent[0].text, "/verify-email")


def test_send_verification_and_verify_email(client, monkeypatch):
    sender = _use_recording_sender(monkeypatch)
    email, resp = _signup(client)
    tokens = _login(client, email)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    sender.sent.clear()  # drop the signup verification email

    resp = client.post("/api/auth/send-verification", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"detail": "Verification email sent"}
    assert len(sender.sent) == 1
    token = _extract_token(sender.sent[0].text, "/verify-email")

    verify_resp = client.post("/api/auth/verify-email", json={"token": token})
    assert verify_resp.status_code == 200, verify_resp.text
    assert verify_resp.json() == {"detail": "Email verified"}

    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200, me.text
    assert me.json()["email_verified"] is True

    # Verifying again with the same (still-valid) token is a no-op, not an error.
    verify_again = client.post("/api/auth/verify-email", json={"token": token})
    assert verify_again.status_code == 200, verify_again.text

    already = client.post("/api/auth/send-verification", headers=headers)
    assert already.status_code == 200, already.text
    assert already.json() == {"detail": "Already verified"}


def test_verify_email_rejects_garbage_token(client):
    resp = client.post("/api/auth/verify-email", json={"token": "not-a-jwt"})
    assert resp.status_code == 400, resp.text


def test_stale_tokens_are_dead_after_account_deletion(client):
    """A deleted account must not be reachable via a pre-deletion verify or refresh token."""
    email, resp = _signup(client)
    user_id = resp.json()["id"]
    tokens = _login(client, email)
    verify_token = create_email_verify_token(user_id)
    refresh_token = create_refresh_token(user_id)

    deleted = client.request(
        "DELETE",
        "/api/profile/me",
        json={"password": PASSWORD},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert deleted.status_code == 204, deleted.text

    resp = client.post("/api/auth/verify-email", json={"token": verify_token})
    assert resp.status_code == 400, resp.text
    resp = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 401, resp.text
