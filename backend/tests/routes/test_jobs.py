"""Tests for jobs: money columns must hold KRW-scale amounts."""

KRW_SALARY_CENTS = 9_500_000_000  # ₩95,000,000 in "cents" — overflows a 32-bit int


def test_job_salary_survives_krw_scale(client, founder):
    resp = client.post(
        "/api/jobs",
        json={
            "title": "ML Engineer (Seoul)",
            "description": "Korean salary band",
            "salary_min": 7_000_000_000,
            "salary_max": KRW_SALARY_CENTS,
            "salary_currency": "KRW",
        },
        headers=founder["headers"],
    )
    assert resp.status_code == 201, resp.text
    job = client.get(f"/api/jobs/{resp.json()['id']}").json()
    assert job["salary_max"] == KRW_SALARY_CENTS


def test_payment_amount_survives_krw_scale(client, founder, applicant):
    resp = client.post(
        "/api/payments",
        json={
            "to_user_id": applicant["user_id"],
            "amount": KRW_SALARY_CENTS,
            "currency": "KRW",
            "payment_type": "salary",
        },
        headers=founder["headers"],
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["amount"] == KRW_SALARY_CENTS
