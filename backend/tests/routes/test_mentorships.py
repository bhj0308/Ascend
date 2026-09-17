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


def _make_mentor(client, user, skills=None, country=None):
    payload = {"mentor_available": True}
    if skills is not None:
        payload["skills"] = skills
    if country is not None:
        payload["country"] = country
    resp = client.put("/api/profile/me", json=payload, headers=user["headers"])
    assert resp.status_code == 200, resp.text
    return resp


def test_mentors_list_excludes_unavailable_and_caller(
    client, founder, applicant, other_user
):
    _make_mentor(client, founder)

    resp = client.get("/api/mentorships/mentors", headers=applicant["headers"])
    assert resp.status_code == 200, resp.text
    ids = [m["id"] for m in resp.json()]
    assert founder["user_id"] in ids
    assert other_user["user_id"] not in ids  # never opted in as a mentor

    # Caller themself is excluded even if they are an available mentor.
    _make_mentor(client, applicant)
    resp = client.get("/api/mentorships/mentors", headers=applicant["headers"])
    assert resp.status_code == 200, resp.text
    assert applicant["user_id"] not in [m["id"] for m in resp.json()]


def test_mentors_list_has_no_email_key(client, founder, applicant):
    _make_mentor(client, founder)
    resp = client.get("/api/mentorships/mentors", headers=applicant["headers"])
    assert resp.status_code == 200, resp.text
    for mentor in resp.json():
        assert "email" not in mentor


def test_mentors_skill_filter_case_insensitive(client, founder, applicant, other_user):
    _make_mentor(client, founder, skills=["Python", "React"])
    _make_mentor(client, other_user, skills=["Go"])

    resp = client.get(
        "/api/mentorships/mentors?skill=python", headers=applicant["headers"]
    )
    assert resp.status_code == 200, resp.text
    ids = [m["id"] for m in resp.json()]
    assert founder["user_id"] in ids
    assert other_user["user_id"] not in ids


def test_mentors_country_filter(client, founder, applicant, other_user):
    _make_mentor(client, founder, country="KR")
    _make_mentor(client, other_user, country="CA")

    resp = client.get(
        "/api/mentorships/mentors?country=kr", headers=applicant["headers"]
    )
    assert resp.status_code == 200, resp.text
    ids = [m["id"] for m in resp.json()]
    assert founder["user_id"] in ids
    assert other_user["user_id"] not in ids


def test_mentors_list_excludes_deleted_accounts(client, founder, applicant):
    _make_mentor(client, founder)

    delete_resp = client.request(
        "DELETE",
        "/api/profile/me",
        json={"password": "hunter22"},
        headers=founder["headers"],
    )
    assert delete_resp.status_code == 204, delete_resp.text

    resp = client.get("/api/mentorships/mentors", headers=applicant["headers"])
    assert resp.status_code == 200, resp.text
    assert founder["user_id"] not in [m["id"] for m in resp.json()]


def _deactivate(client, user):
    resp = client.request(
        "DELETE",
        "/api/profile/me",
        json={"password": "hunter22"},
        headers=user["headers"],
    )
    assert resp.status_code == 204, resp.text


def test_request_mentorship_from_deleted_account_rejected(client, founder, other_user):
    _deactivate(client, other_user)
    resp = client.post(
        "/api/mentorships",
        json={"mentor_id": other_user["user_id"]},
        headers=founder["headers"],
    )
    assert resp.status_code == 400, resp.text
    assert "no longer active" in resp.json()["detail"]


def test_accept_after_mentee_deleted_rejected(client, founder, applicant):
    created = _request_mentorship(client, applicant, founder)
    mentorship_id = created.json()["id"]
    _deactivate(client, applicant)

    resp = client.post(
        f"/api/mentorships/{mentorship_id}/accept", headers=founder["headers"]
    )
    assert resp.status_code == 400, resp.text
    assert "no longer active" in resp.json()["detail"]
