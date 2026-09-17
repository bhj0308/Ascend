"""Tests for the Messages API: send, thread list, and per-user history."""


def _send(client, sender, recipient_id, body="hello", job_id=None):
    payload = {"recipient_id": recipient_id, "body": body}
    if job_id is not None:
        payload["job_id"] = job_id
    return client.post("/api/messages", json=payload, headers=sender["headers"])


def test_send_message_happy_path(client, founder, applicant):
    resp = _send(client, founder, applicant["user_id"], body="  hi there  ")
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["sender_id"] == founder["user_id"]
    assert body["recipient_id"] == applicant["user_id"]
    assert body["body"] == "hi there"
    assert body["read"] is False
    assert body["job_id"] is None


def test_send_message_to_self_rejected(client, founder):
    resp = _send(client, founder, founder["user_id"])
    assert resp.status_code == 400, resp.text


def test_send_message_empty_body_rejected(client, founder, applicant):
    resp = _send(client, founder, applicant["user_id"], body="   ")
    assert resp.status_code == 400, resp.text


def test_send_message_unknown_recipient_rejected(client, founder):
    resp = _send(client, founder, 9_999_999)
    assert resp.status_code == 404, resp.text


def test_send_message_unknown_job_rejected(client, founder, applicant):
    resp = _send(client, founder, applicant["user_id"], job_id=9_999_999)
    assert resp.status_code == 404, resp.text


def test_send_message_with_valid_job(client, founder, applicant):
    job_resp = client.post(
        "/api/jobs",
        json={"title": "Backend Engineer", "description": "Build things."},
        headers=founder["headers"],
    )
    assert job_resp.status_code == 201, job_resp.text
    job_id = job_resp.json()["id"]

    resp = _send(client, founder, applicant["user_id"], job_id=job_id)
    assert resp.status_code == 201, resp.text
    assert resp.json()["job_id"] == job_id


def test_threads_shows_counterpart_once_with_unread_and_last_message(
    client, founder, applicant
):
    _send(client, founder, applicant["user_id"], body="first")
    _send(client, founder, applicant["user_id"], body="second")
    _send(client, applicant, founder["user_id"], body="reply")

    resp = client.get("/api/messages/threads", headers=founder["headers"])
    assert resp.status_code == 200, resp.text
    threads = resp.json()
    assert len(threads) == 1
    thread = threads[0]
    assert thread["user_id"] == applicant["user_id"]
    assert thread["last_message_body"] == "reply"
    assert thread["unread_count"] == 1  # the one unread reply from applicant


def test_threads_empty_for_third_party(client, founder, applicant, other_user):
    _send(client, founder, applicant["user_id"], body="hi")

    resp = client.get("/api/messages/threads", headers=other_user["headers"])
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_thread_with_user_returns_ascending_both_directions(client, founder, applicant):
    _send(client, founder, applicant["user_id"], body="one")
    _send(client, applicant, founder["user_id"], body="two")
    _send(client, founder, applicant["user_id"], body="three")

    resp = client.get(
        f"/api/messages/with/{applicant['user_id']}", headers=founder["headers"]
    )
    assert resp.status_code == 200, resp.text
    bodies = [m["body"] for m in resp.json()]
    assert bodies == ["one", "two", "three"]


def test_opening_thread_marks_read_and_updates_unread_counts(
    client, founder, applicant
):
    _send(client, founder, applicant["user_id"], body="one")
    _send(client, founder, applicant["user_id"], body="two")
    _send(client, applicant, founder["user_id"], body="reply")

    # Applicant opens the thread with founder: marks founder->applicant read.
    resp = client.get(
        f"/api/messages/with/{founder['user_id']}", headers=applicant["headers"]
    )
    assert resp.status_code == 200, resp.text
    assert all(m["read"] for m in resp.json() if m["sender_id"] == founder["user_id"])

    applicant_threads = {
        t["user_id"]: t
        for t in client.get(
            "/api/messages/threads", headers=applicant["headers"]
        ).json()
    }
    assert applicant_threads[founder["user_id"]]["unread_count"] == 0

    # Founder's unread count for applicant's reply is unaffected.
    founder_threads = {
        t["user_id"]: t
        for t in client.get("/api/messages/threads", headers=founder["headers"]).json()
    }
    assert founder_threads[applicant["user_id"]]["unread_count"] == 1


def test_thread_with_unknown_user_returns_404(client, founder):
    resp = client.get("/api/messages/with/9999999", headers=founder["headers"])
    assert resp.status_code == 404, resp.text


def test_thread_with_user_visible_to_third_party_is_empty_not_forbidden(
    client, founder, applicant, other_user
):
    _send(client, founder, applicant["user_id"], body="private")

    resp = client.get(
        f"/api/messages/with/{founder['user_id']}", headers=other_user["headers"]
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == []
