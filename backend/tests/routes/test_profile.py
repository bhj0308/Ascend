"""Tests for profiles: what is private to the owner vs. visible to other users."""

import re

from app.models.user import User, UserStatus
from tests.conftest import TestingSessionLocal


def test_public_profile_never_exposes_email(client, founder, applicant):
    resp = client.get(
        f"/api/profile/{applicant['user_id']}", headers=founder["headers"]
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["id"] == applicant["user_id"]
    assert "email" not in body
    assert "password_hash" not in body
    assert "phone" not in body


def test_own_profile_includes_email(client, applicant):
    resp = client.get("/api/profile/me", headers=applicant["headers"])
    assert resp.status_code == 200, resp.text
    assert "email" in resp.json()
    assert "password_hash" not in resp.json()


def test_timestamps_are_timezone_aware(client, applicant):
    """Naive timestamps get parsed as local time by browsers; we must emit an offset."""
    resp = client.get("/api/profile/me", headers=applicant["headers"])
    assert resp.status_code == 200, resp.text
    created_at = resp.json()["created_at"]
    assert re.search(r"(Z|[+-]\d\d:\d\d)$", created_at), created_at


def test_update_mentor_available_visible_to_others(client, founder, applicant):
    resp = client.put(
        "/api/profile/me",
        json={"mentor_available": True},
        headers=founder["headers"],
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["mentor_available"] is True

    resp = client.get(
        f"/api/profile/{founder['user_id']}", headers=applicant["headers"]
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["mentor_available"] is True


def test_delete_account_wrong_password(client, founder):
    resp = client.request(
        "DELETE",
        "/api/profile/me",
        json={"password": "wrong-password"},
        headers=founder["headers"],
    )
    assert resp.status_code == 401, resp.text


def test_delete_account_no_password_hash(client, founder):
    """A user with no password (e.g. OAuth-only) can't delete via this flow."""
    db = TestingSessionLocal()
    try:
        from app.models.user import User

        user = db.query(User).filter(User.id == founder["user_id"]).first()
        user.password_hash = None
        db.commit()
    finally:
        db.close()

    resp = client.request(
        "DELETE",
        "/api/profile/me",
        json={"password": "hunter22"},
        headers=founder["headers"],
    )
    assert resp.status_code == 400, resp.text


def test_delete_account_success(client, founder, applicant):
    # founder posts an open job and gets a message from applicant, so we can
    # check the side effects of deletion on both.
    job_resp = client.post(
        "/api/jobs",
        json={"title": "Backend Engineer", "description": "Build things"},
        headers=founder["headers"],
    )
    assert job_resp.status_code == 201, job_resp.text
    job_id = job_resp.json()["id"]

    message_resp = client.post(
        "/api/messages",
        json={"recipient_id": founder["user_id"], "body": "Hi there"},
        headers=applicant["headers"],
    )
    assert message_resp.status_code == 201, message_resp.text

    me_before = client.get("/api/profile/me", headers=founder["headers"])
    founder_email = me_before.json()["email"]

    delete_resp = client.request(
        "DELETE",
        "/api/profile/me",
        json={"password": "hunter22"},
        headers=founder["headers"],
    )
    assert delete_resp.status_code == 204, delete_resp.text

    # Old token is now rejected everywhere.
    me_resp = client.get("/api/auth/me", headers=founder["headers"])
    assert me_resp.status_code == 401, me_resp.text

    # Old credentials no longer log in (password cleared).
    login_resp = client.post(
        "/api/auth/login",
        json={"email": founder_email, "password": "hunter22"},
    )
    assert login_resp.status_code == 401, login_resp.text

    # Public profile is scrubbed but still resolvable by id.
    public_resp = client.get(
        f"/api/profile/{founder['user_id']}", headers=applicant["headers"]
    )
    assert public_resp.status_code == 200, public_resp.text
    public_body = public_resp.json()
    assert public_body["first_name"] is None
    assert "email" not in public_body

    # Their previously open job is now closed.
    job_check = client.get(f"/api/jobs/{job_id}", headers=applicant["headers"])
    assert job_check.status_code == 200, job_check.text
    assert job_check.json()["status"] == "closed"

    # The message thread shows the fallback display name.
    threads_resp = client.get("/api/messages/threads", headers=applicant["headers"])
    assert threads_resp.status_code == 200, threads_resp.text
    thread = next(t for t in threads_resp.json() if t["user_id"] == founder["user_id"])
    assert thread["user_name"] == f"User #{founder['user_id']}"


def test_delete_account_clears_every_identity_field(client, founder):
    """None of these are exposed by any response, so check the row directly."""
    resp = client.request(
        "DELETE",
        "/api/profile/me",
        json={"password": "hunter22"},
        headers=founder["headers"],
    )
    assert resp.status_code == 204, resp.text

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.id == founder["user_id"]).one()
        assert user.status == UserStatus.INACTIVE
        assert user.email == f"deleted-{user.id}@deleted.invalid"
        for field in (
            "first_name",
            "last_name",
            "bio",
            "avatar_url",
            "phone",
            "city",
            "country",
            "skills",
            "languages",
            "visa_status",
            "visa_expiry",
            "timezone",
            "password_hash",
            "google_id",
            "github_id",
        ):
            assert getattr(user, field) is None, field
        assert user.email_verified is False
        assert user.mentor_available is False
    finally:
        db.close()
