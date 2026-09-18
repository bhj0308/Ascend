"""Admin moderation: who may moderate, suspending accounts, closing jobs."""


def _post_job(client, actor, title="Spam job"):
    resp = client.post(
        "/api/jobs",
        headers=actor["headers"],
        json={"title": title, "description": "Buy my course", "job_type": "full_time"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_signup_cannot_self_assign_admin(client):
    resp = client.post(
        "/api/auth/signup",
        json={
            "email": "wannabe-admin@example.com",
            "password": "hunter22",
            "user_type": "admin",
            "first_name": "Wannabe",
        },
    )
    assert resp.status_code == 422, resp.text
    assert "admin" in resp.text


def test_profile_update_cannot_grant_admin(client, applicant):
    resp = client.put(
        "/api/profile/me",
        headers=applicant["headers"],
        json={"first_name": "Still", "user_type": "admin", "status": "active"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["user_type"] == "engineer"


def test_admin_routes_reject_non_admins(client, founder):
    for method, path in [
        ("get", "/api/admin/users"),
        ("get", "/api/admin/jobs"),
        ("post", "/api/admin/users/1/suspend"),
        ("post", "/api/admin/users/1/unsuspend"),
        ("post", "/api/admin/jobs/1/close"),
    ]:
        resp = getattr(client, method)(path, headers=founder["headers"])
        assert resp.status_code == 403, f"{method} {path}: {resp.text}"
        assert resp.json()["detail"] == "Admin access required"


def test_admin_routes_require_authentication(client):
    assert client.get("/api/admin/users").status_code == 401


def test_admin_lists_and_searches_users(client, admin, applicant):
    resp = client.get("/api/admin/users", headers=admin["headers"])
    assert resp.status_code == 200, resp.text
    assert applicant["user_id"] in [u["id"] for u in resp.json()]

    resp = client.get(
        "/api/admin/users", headers=admin["headers"], params={"q": applicant["email"]}
    )
    assert resp.status_code == 200, resp.text
    assert [u["id"] for u in resp.json()] == [applicant["user_id"]]


def test_suspending_a_user_blocks_them_and_closes_their_jobs(client, admin, founder):
    job = _post_job(client, founder)

    resp = client.post(
        f"/api/admin/users/{founder['user_id']}/suspend", headers=admin["headers"]
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "suspended"

    # Their session stops working immediately.
    assert client.get("/api/auth/me", headers=founder["headers"]).status_code == 401
    # And logging back in is refused, with a reason.
    login = client.post(
        "/api/auth/login",
        json={"email": founder["email"], "password": founder["password"]},
    )
    assert login.status_code == 403, login.text
    assert login.json()["detail"] == "This account has been suspended"

    # The job is off the public board.
    assert job["id"] not in [j["id"] for j in client.get("/api/jobs").json()]
    assert client.get(f"/api/jobs/{job['id']}").json()["status"] == "closed"


def test_unsuspend_restores_access(client, admin, founder):
    client.post(
        f"/api/admin/users/{founder['user_id']}/suspend", headers=admin["headers"]
    )
    resp = client.post(
        f"/api/admin/users/{founder['user_id']}/unsuspend", headers=admin["headers"]
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "active"

    login = client.post(
        "/api/auth/login",
        json={"email": founder["email"], "password": founder["password"]},
    )
    assert login.status_code == 200, login.text


def test_unsuspend_rejects_an_active_account(client, admin, founder):
    resp = client.post(
        f"/api/admin/users/{founder['user_id']}/unsuspend", headers=admin["headers"]
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Account is not suspended"


def test_admin_cannot_suspend_themselves(client, admin):
    resp = client.post(
        f"/api/admin/users/{admin['user_id']}/suspend", headers=admin["headers"]
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "You cannot suspend yourself"


def test_suspend_unknown_user_is_404(client, admin):
    assert (
        client.post(
            "/api/admin/users/999999/suspend", headers=admin["headers"]
        ).status_code
        == 404
    )


def test_suspending_a_deleted_account_is_rejected(client, admin, applicant):
    deleted = client.request(
        "DELETE",
        "/api/profile/me",
        headers=applicant["headers"],
        json={"password": applicant["password"]},
    )
    assert deleted.status_code == 204, deleted.text

    resp = client.post(
        f"/api/admin/users/{applicant['user_id']}/suspend", headers=admin["headers"]
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Account is already deleted"


def test_admin_closes_a_job(client, admin, founder):
    job = _post_job(client, founder)

    resp = client.post(f"/api/admin/jobs/{job['id']}/close", headers=admin["headers"])
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "closed"
    assert job["id"] not in [j["id"] for j in client.get("/api/jobs").json()]

    # Closing twice is a no-op error, not a silent success.
    again = client.post(f"/api/admin/jobs/{job['id']}/close", headers=admin["headers"])
    assert again.status_code == 400
    assert again.json()["detail"] == "Job is already closed"


def test_admin_job_list_includes_closed_jobs(client, admin, founder):
    job = _post_job(client, founder, title="Closed listing")
    client.post(f"/api/admin/jobs/{job['id']}/close", headers=admin["headers"])

    resp = client.get(
        "/api/admin/jobs", headers=admin["headers"], params={"q": "Closed listing"}
    )
    assert resp.status_code == 200, resp.text
    assert [j["id"] for j in resp.json()] == [job["id"]]


def test_close_unknown_job_is_404(client, admin):
    assert (
        client.post(
            "/api/admin/jobs/999999/close", headers=admin["headers"]
        ).status_code
        == 404
    )
