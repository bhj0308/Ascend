"""Tests for the Mentorships API: request, and the accept/decline/complete lifecycle."""


def _request_mentorship(client, mentee, mentor, notes=None):
    return client.post(
        "/api/mentorships",
        json={"mentor_id": mentor["user_id"], "notes": notes},
        headers=mentee["headers"],
    )


def test_request_mentorship_happy_path(client, founder, applicant):
    resp = _request_mentorship(client, applicant, founder, notes="Please help")
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "requested"
    assert body["mentor_id"] == founder["user_id"]
    assert body["mentee_id"] == applicant["user_id"]
    assert body["notes"] == "Please help"
    assert body["mentor_name"]
    assert body["mentee_name"]


def test_request_mentorship_with_self_rejected(client, founder):
    resp = _request_mentorship(client, founder, founder)
    assert resp.status_code == 400, resp.text


def test_request_mentorship_unknown_mentor_not_found(client, applicant):
    resp = client.post(
        "/api/mentorships",
        json={"mentor_id": 999999},
        headers=applicant["headers"],
    )
    assert resp.status_code == 404, resp.text


def test_duplicate_request_while_requested_rejected(client, founder, applicant):
    first = _request_mentorship(client, applicant, founder)
    assert first.status_code == 201, first.text

    second = _request_mentorship(client, applicant, founder)
    assert second.status_code == 400, second.text


def test_duplicate_request_reverse_direction_while_active_rejected(
    client, founder, applicant
):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]

    accepted = client.post(
        f"/api/mentorships/{mentorship_id}/accept", headers=founder["headers"]
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["status"] == "active"

    # applicant is now mentee of an ACTIVE relationship; reverse direction
    # (applicant tries to become founder's mentor) should still be blocked.
    reverse = _request_mentorship(client, founder, applicant)
    assert reverse.status_code == 400, reverse.text


def test_my_mentorships_visible_to_both_parties_empty_for_third_party(
    client, founder, applicant, other_user
):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]

    for party in (founder, applicant):
        resp = client.get("/api/mentorships/me", headers=party["headers"])
        assert resp.status_code == 200, resp.text
        assert [m["id"] for m in resp.json()] == [mentorship_id]

    resp = client.get("/api/mentorships/me", headers=other_user["headers"])
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_get_mentorship_by_third_party_forbidden(
    client, founder, applicant, other_user
):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]

    resp = client.get(
        f"/api/mentorships/{mentorship_id}", headers=other_user["headers"]
    )
    assert resp.status_code == 403, resp.text


def test_accept_by_mentee_forbidden(client, founder, applicant):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]

    resp = client.post(
        f"/api/mentorships/{mentorship_id}/accept", headers=applicant["headers"]
    )
    assert resp.status_code == 403, resp.text


def test_accept_by_mentor_activates(client, founder, applicant):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]

    resp = client.post(
        f"/api/mentorships/{mentorship_id}/accept", headers=founder["headers"]
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "active"


def test_accept_twice_rejected(client, founder, applicant):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]

    client.post(f"/api/mentorships/{mentorship_id}/accept", headers=founder["headers"])
    resp = client.post(
        f"/api/mentorships/{mentorship_id}/accept", headers=founder["headers"]
    )
    assert resp.status_code == 400, resp.text


def test_decline_flow(client, founder, applicant):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]

    resp = client.post(
        f"/api/mentorships/{mentorship_id}/decline", headers=founder["headers"]
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "declined"


def test_decline_by_mentee_forbidden(client, founder, applicant):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]

    resp = client.post(
        f"/api/mentorships/{mentorship_id}/decline", headers=applicant["headers"]
    )
    assert resp.status_code == 403, resp.text


def test_complete_while_requested_rejected(client, founder, applicant):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]

    resp = client.post(
        f"/api/mentorships/{mentorship_id}/complete", headers=founder["headers"]
    )
    assert resp.status_code == 400, resp.text


def test_complete_by_mentee_after_accept(client, founder, applicant):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]

    client.post(f"/api/mentorships/{mentorship_id}/accept", headers=founder["headers"])

    resp = client.post(
        f"/api/mentorships/{mentorship_id}/complete", headers=applicant["headers"]
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "completed"


def test_complete_by_third_party_forbidden(client, founder, applicant, other_user):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]

    client.post(f"/api/mentorships/{mentorship_id}/accept", headers=founder["headers"])

    resp = client.post(
        f"/api/mentorships/{mentorship_id}/complete", headers=other_user["headers"]
    )
    assert resp.status_code == 403, resp.text
