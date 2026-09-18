"""Actions that reach other users require a verified email.

The gate is controlled by REQUIRE_EMAIL_VERIFICATION, which is on by default
but off in production until an email provider is configured.
"""

import pytest

from app.config import get_settings

GATED = "Verify your email address before doing this"


@pytest.fixture()
def verification_disabled():
    settings = get_settings()
    settings.REQUIRE_EMAIL_VERIFICATION = False
    try:
        yield
    finally:
        settings.REQUIRE_EMAIL_VERIFICATION = True


def _open_job(client, founder):
    resp = client.post(
        "/api/jobs",
        headers=founder["headers"],
        json={
            "title": "Backend Engineer",
            "description": "Build things",
            "job_type": "full_time",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_unverified_user_cannot_post_a_job(client, unverified_user):
    resp = client.post(
        "/api/jobs",
        headers=unverified_user["headers"],
        json={"title": "Spam", "description": "...", "job_type": "full_time"},
    )
    assert resp.status_code == 403, resp.text
    assert resp.json()["detail"] == GATED


def test_unverified_user_cannot_apply(client, founder, unverified_user):
    job = _open_job(client, founder)
    resp = client.post(
        "/api/applications",
        headers=unverified_user["headers"],
        json={"job_id": job["id"], "cover_note": "hire me"},
    )
    assert resp.status_code == 403, resp.text
    assert resp.json()["detail"] == GATED


def test_unverified_user_cannot_message(client, founder, unverified_user):
    resp = client.post(
        "/api/messages",
        headers=unverified_user["headers"],
        json={"recipient_id": founder["user_id"], "body": "hello"},
    )
    assert resp.status_code == 403, resp.text
    assert resp.json()["detail"] == GATED


def test_unverified_user_cannot_request_mentorship(client, founder, unverified_user):
    resp = client.post(
        "/api/mentorships",
        headers=unverified_user["headers"],
        json={"mentor_id": founder["user_id"]},
    )
    assert resp.status_code == 403, resp.text
    assert resp.json()["detail"] == GATED


def test_unverified_user_can_still_read_and_edit_their_own_profile(
    client, unverified_user
):
    assert (
        client.get("/api/auth/me", headers=unverified_user["headers"]).status_code
        == 200
    )
    assert client.get("/api/jobs").status_code == 200
    resp = client.put(
        "/api/profile/me", headers=unverified_user["headers"], json={"bio": "Hello"}
    )
    assert resp.status_code == 200, resp.text


def test_verifying_the_email_unblocks_posting(client, unverified_user):
    from app.services.auth import create_email_verify_token

    blocked = client.post(
        "/api/jobs",
        headers=unverified_user["headers"],
        json={
            "title": "Backend Engineer",
            "description": "Build things",
            "job_type": "full_time",
        },
    )
    assert blocked.status_code == 403

    verify = client.post(
        "/api/auth/verify-email",
        json={"token": create_email_verify_token(unverified_user["user_id"])},
    )
    assert verify.status_code == 200, verify.text

    allowed = client.post(
        "/api/jobs",
        headers=unverified_user["headers"],
        json={
            "title": "Backend Engineer",
            "description": "Build things",
            "job_type": "full_time",
        },
    )
    assert allowed.status_code == 201, allowed.text


def test_gate_is_off_when_the_flag_is_disabled(
    client, unverified_user, verification_disabled
):
    resp = client.post(
        "/api/jobs",
        headers=unverified_user["headers"],
        json={
            "title": "Backend Engineer",
            "description": "Build things",
            "job_type": "full_time",
        },
    )
    assert resp.status_code == 201, resp.text
