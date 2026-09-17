"""Tests for the Payments API: creation and the pending/cancel/execute lifecycle.

Money does not move in this version; these tests only exercise status
transitions and authorization.
"""

from uuid import uuid4


def _create_payment(client, sender, **overrides):
    payload = {
        "amount": 50000,
        "currency": "cad",
        "payment_type": "remittance",
    }
    payload.update(overrides)
    return client.post("/api/payments", json=payload, headers=sender["headers"])


def test_create_payment_to_platform_user(client, founder, applicant):
    resp = _create_payment(client, founder, to_user_id=applicant["user_id"])
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "pending"
    assert body["from_user_id"] == founder["user_id"]
    assert body["to_user_id"] == applicant["user_id"]
    assert body["currency"] == "CAD"
    assert body["from_user_name"] == "Test Founder"
    assert body["to_user_name"] == "Test Engineer"


def test_create_payment_to_external_email(client, founder):
    resp = _create_payment(
        client,
        founder,
        recipient_email="grandma@example.com",
        recipient_name="Grandma",
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["to_user_id"] is None
    assert body["recipient_email"] == "grandma@example.com"
    assert body["to_user_name"] is None


def test_create_payment_with_both_to_user_id_and_email_rejected(
    client, founder, applicant
):
    resp = _create_payment(
        client,
        founder,
        to_user_id=applicant["user_id"],
        recipient_email="grandma@example.com",
    )
    assert resp.status_code == 400, resp.text


def test_create_payment_with_neither_target_rejected(client, founder):
    resp = _create_payment(client, founder)
    assert resp.status_code == 400, resp.text


def test_create_payment_to_self_rejected(client, founder):
    resp = _create_payment(client, founder, to_user_id=founder["user_id"])
    assert resp.status_code == 400, resp.text


def test_create_payment_to_unknown_user_not_found(client, founder):
    resp = _create_payment(client, founder, to_user_id=999999999)
    assert resp.status_code == 404, resp.text


def test_create_payment_zero_amount_rejected(client, founder, applicant):
    resp = _create_payment(client, founder, to_user_id=applicant["user_id"], amount=0)
    assert resp.status_code == 422, resp.text


def test_my_payments_visible_to_parties_only(client, founder, applicant, other_user):
    payment_id = _create_payment(
        client, founder, to_user_id=applicant["user_id"]
    ).json()["id"]

    for party in (founder, applicant):
        resp = client.get("/api/payments/me", headers=party["headers"])
        assert resp.status_code == 200, resp.text
        assert [p["id"] for p in resp.json()] == [payment_id]

    resp = client.get("/api/payments/me", headers=other_user["headers"])
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_get_payment_by_third_party_forbidden(client, founder, applicant, other_user):
    payment_id = _create_payment(
        client, founder, to_user_id=applicant["user_id"]
    ).json()["id"]

    resp = client.get(f"/api/payments/{payment_id}", headers=other_user["headers"])
    assert resp.status_code == 403, resp.text


def test_cancel_payment_by_recipient_forbidden(client, founder, applicant):
    payment_id = _create_payment(
        client, founder, to_user_id=applicant["user_id"]
    ).json()["id"]

    resp = client.post(
        f"/api/payments/{payment_id}/cancel", headers=applicant["headers"]
    )
    assert resp.status_code == 403, resp.text


def test_cancel_payment_happy_path_then_cancel_again_rejected(
    client, founder, applicant
):
    payment_id = _create_payment(
        client, founder, to_user_id=applicant["user_id"]
    ).json()["id"]

    resp = client.post(f"/api/payments/{payment_id}/cancel", headers=founder["headers"])
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "cancelled"

    resp = client.post(f"/api/payments/{payment_id}/cancel", headers=founder["headers"])
    assert resp.status_code == 400, resp.text


def test_execute_payment_by_recipient_forbidden(client, founder, applicant):
    payment_id = _create_payment(
        client, founder, to_user_id=applicant["user_id"]
    ).json()["id"]

    resp = client.post(
        f"/api/payments/{payment_id}/execute", headers=applicant["headers"]
    )
    assert resp.status_code == 403, resp.text


def test_execute_payment_with_flag_off_returns_501_and_stays_pending(
    client, founder, applicant
):
    payment_id = _create_payment(
        client, founder, to_user_id=applicant["user_id"]
    ).json()["id"]

    resp = client.post(
        f"/api/payments/{payment_id}/execute", headers=founder["headers"]
    )
    assert resp.status_code == 501, resp.text

    check = client.get(f"/api/payments/{payment_id}", headers=founder["headers"])
    assert check.json()["status"] == "pending"


def test_recipient_without_name_falls_back_to_email_local_part(client, founder):
    """conftest always sets names; cover the blank-name display path explicitly."""
    local_part = f"noname-{uuid4().hex[:8]}"
    signup = client.post(
        "/api/auth/signup",
        json={
            "email": f"{local_part}@example.com",
            "password": "testpass123",
            "user_type": "engineer",
        },
    )
    assert signup.status_code == 201, signup.text

    resp = _create_payment(client, founder, to_user_id=signup.json()["id"])
    assert resp.status_code == 201, resp.text
    assert resp.json()["to_user_name"] == local_part
