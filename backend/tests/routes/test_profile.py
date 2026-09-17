"""Tests for profiles: what is private to the owner vs. visible to other users."""

import re


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
