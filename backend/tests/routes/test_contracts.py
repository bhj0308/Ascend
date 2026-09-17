"""Tests for the Contracts API: template listing, generation, and lifecycle."""

TEMPLATE_TYPE = "korea_engineer_canada_co"

VALID_TERMS = {
    "salary": 8000000,
    "currency": "CAD",
    "start_date": "2026-01-01",
    "work_location_country": "KR",
    "payment_schedule": "monthly",
}


def _create_job(client, founder):
    resp = client.post(
        "/api/jobs",
        json={"title": "Backend Engineer", "description": "Build things."},
        headers=founder["headers"],
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_application(client, founder, applicant):
    job_id = _create_job(client, founder)
    resp = client.post(
        "/api/applications",
        json={"job_id": job_id, "cover_note": "Hi"},
        headers=applicant["headers"],
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"], job_id


def _create_contract(client, founder, application_id, terms=None):
    return client.post(
        "/api/contracts",
        json={
            "application_id": application_id,
            "template_type": TEMPLATE_TYPE,
            "terms": terms if terms is not None else VALID_TERMS,
        },
        headers=founder["headers"],
    )


def test_list_templates(client, founder):
    resp = client.get("/api/contracts/templates", headers=founder["headers"])
    assert resp.status_code == 200, resp.text
    templates = resp.json()
    types = {t["type"] for t in templates}
    assert TEMPLATE_TYPE in types
    korea_template = next(t for t in templates if t["type"] == TEMPLATE_TYPE)
    assert "salary" in korea_template["required_terms"]
    assert "currency" in korea_template["required_terms"]
    assert "start_date" in korea_template["required_terms"]
    assert korea_template["label"]
    assert korea_template["description"]


def test_create_contract_happy_path(client, founder, applicant):
    application_id, job_id = _create_application(client, founder, applicant)
    resp = _create_contract(client, founder, application_id)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "draft"
    assert body["job_id"] == job_id
    assert body["job_title"] == "Backend Engineer"
    assert body["founder_id"] == founder["user_id"]
    assert body["applicant_id"] == applicant["user_id"]
    assert body["terms"] == VALID_TERMS


def test_create_contract_by_non_creator_forbidden(
    client, founder, applicant, other_user
):
    application_id, _ = _create_application(client, founder, applicant)
    resp = _create_contract(client, other_user, application_id)
    assert resp.status_code == 403, resp.text


def test_create_duplicate_contract_rejected(client, founder, applicant):
    application_id, _ = _create_application(client, founder, applicant)
    first = _create_contract(client, founder, application_id)
    assert first.status_code == 201, first.text

    second = _create_contract(client, founder, application_id)
    assert second.status_code == 400, second.text
    assert "already has a contract" in second.json()["detail"]


def test_create_contract_missing_required_term(client, founder, applicant):
    application_id, _ = _create_application(client, founder, applicant)
    incomplete_terms = {"salary": 8000000, "currency": "CAD"}  # missing start_date etc.
    resp = _create_contract(client, founder, application_id, terms=incomplete_terms)
    assert resp.status_code == 400, resp.text
    assert "start_date" in resp.json()["detail"]


def test_get_contract_by_unrelated_user_forbidden(
    client, founder, applicant, other_user
):
    application_id, _ = _create_application(client, founder, applicant)
    created = _create_contract(client, founder, application_id)
    contract_id = created.json()["id"]

    resp = client.get(f"/api/contracts/{contract_id}", headers=other_user["headers"])
    assert resp.status_code == 403, resp.text


def test_sign_before_send_rejected(client, founder, applicant):
    application_id, _ = _create_application(client, founder, applicant)
    created = _create_contract(client, founder, application_id)
    contract_id = created.json()["id"]

    resp = client.post(
        f"/api/contracts/{contract_id}/sign", headers=applicant["headers"]
    )
    assert resp.status_code == 400, resp.text


def test_send_by_applicant_forbidden(client, founder, applicant):
    application_id, _ = _create_application(client, founder, applicant)
    created = _create_contract(client, founder, application_id)
    contract_id = created.json()["id"]

    resp = client.post(
        f"/api/contracts/{contract_id}/send", headers=applicant["headers"]
    )
    assert resp.status_code == 403, resp.text


def test_send_then_sign_happy_flow(client, founder, applicant):
    application_id, _ = _create_application(client, founder, applicant)
    created = _create_contract(client, founder, application_id)
    contract_id = created.json()["id"]

    sent = client.post(f"/api/contracts/{contract_id}/send", headers=founder["headers"])
    assert sent.status_code == 200, sent.text
    assert sent.json()["status"] == "pending_signature"

    signed = client.post(
        f"/api/contracts/{contract_id}/sign", headers=applicant["headers"]
    )
    assert signed.status_code == 200, signed.text
    body = signed.json()
    assert body["status"] == "signed"
    assert body["signed_at"] is not None


def test_founder_sign_forbidden(client, founder, applicant):
    application_id, _ = _create_application(client, founder, applicant)
    created = _create_contract(client, founder, application_id)
    contract_id = created.json()["id"]

    client.post(f"/api/contracts/{contract_id}/send", headers=founder["headers"])

    resp = client.post(f"/api/contracts/{contract_id}/sign", headers=founder["headers"])
    assert resp.status_code == 403, resp.text


def test_cancel_after_signed_rejected(client, founder, applicant):
    application_id, _ = _create_application(client, founder, applicant)
    created = _create_contract(client, founder, application_id)
    contract_id = created.json()["id"]

    client.post(f"/api/contracts/{contract_id}/send", headers=founder["headers"])
    client.post(f"/api/contracts/{contract_id}/sign", headers=applicant["headers"])

    resp = client.post(
        f"/api/contracts/{contract_id}/cancel", headers=founder["headers"]
    )
    assert resp.status_code == 400, resp.text


# --- PUT /{id} ---------------------------------------------------------------


def test_update_terms_by_applicant_forbidden(client, founder, applicant):
    application_id, _ = _create_application(client, founder, applicant)
    contract_id = _create_contract(client, founder, application_id).json()["id"]

    resp = client.put(
        f"/api/contracts/{contract_id}",
        json={"terms": VALID_TERMS},
        headers=applicant["headers"],
    )
    assert resp.status_code == 403, resp.text


def test_update_terms_happy_path_and_revalidates(client, founder, applicant):
    application_id, _ = _create_application(client, founder, applicant)
    contract_id = _create_contract(client, founder, application_id).json()["id"]

    new_terms = {**VALID_TERMS, "salary": 9000000}
    resp = client.put(
        f"/api/contracts/{contract_id}",
        json={"terms": new_terms},
        headers=founder["headers"],
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["terms"]["salary"] == 9000000

    incomplete = {"salary": 9000000, "currency": "CAD"}
    resp = client.put(
        f"/api/contracts/{contract_id}",
        json={"terms": incomplete},
        headers=founder["headers"],
    )
    assert resp.status_code == 400, resp.text
    assert "start_date" in resp.json()["detail"]


def test_update_terms_after_send_rejected(client, founder, applicant):
    application_id, _ = _create_application(client, founder, applicant)
    contract_id = _create_contract(client, founder, application_id).json()["id"]
    client.post(f"/api/contracts/{contract_id}/send", headers=founder["headers"])

    resp = client.put(
        f"/api/contracts/{contract_id}",
        json={"terms": VALID_TERMS},
        headers=founder["headers"],
    )
    assert resp.status_code == 400, resp.text


# --- GET /me -----------------------------------------------------------------


def test_my_contracts_visible_to_parties_only(client, founder, applicant, other_user):
    application_id, _ = _create_application(client, founder, applicant)
    contract_id = _create_contract(client, founder, application_id).json()["id"]

    for party in (founder, applicant):
        resp = client.get("/api/contracts/me", headers=party["headers"])
        assert resp.status_code == 200, resp.text
        assert [c["id"] for c in resp.json()] == [contract_id]

    resp = client.get("/api/contracts/me", headers=other_user["headers"])
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


# --- term type validation ----------------------------------------------------


def test_create_contract_rejects_wrong_typed_terms(client, founder, applicant):
    application_id, _ = _create_application(client, founder, applicant)
    gig_terms = {
        "hourly_rate": 4500,
        "currency": "CAD",
        "start_date": "2026-01-01",
        "hours_per_week": 20,
    }

    def create(terms):
        return client.post(
            "/api/contracts",
            json={
                "application_id": application_id,
                "template_type": "part_time_gig",
                "terms": terms,
            },
            headers=founder["headers"],
        )

    resp = create({**gig_terms, "hourly_rate": "not_a_number"})
    assert resp.status_code == 400, resp.text
    assert "hourly_rate" in resp.json()["detail"]

    resp = create({**gig_terms, "hourly_rate": 45.5})
    assert resp.status_code == 400, resp.text

    resp = create({**gig_terms, "hours_per_week": "ten"})
    assert resp.status_code == 400, resp.text
    assert "hours_per_week" in resp.json()["detail"]

    resp = create(gig_terms)
    assert resp.status_code == 201, resp.text


def test_route_specific_404_detail_is_preserved(client, founder):
    """A global 404 handler once overwrote every 404 detail with 'Endpoint not found'."""
    resp = client.get("/api/contracts/9999999", headers=founder["headers"])
    assert resp.status_code == 404, resp.text
    assert resp.json()["detail"] == "Contract not found"
