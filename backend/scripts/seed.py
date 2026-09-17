"""Seed a realistic demo dataset so the MVP is interactable.

Usage (from backend/, venv active, DATABASE_URL from .env):
    python scripts/seed.py                    # seed; refuses if demo data exists
    python scripts/seed.py --reset            # remove demo rows (FK order), then seed
    python scripts/seed.py --allow-production # required when ENVIRONMENT=production

Everything is created through the real API (in-process TestClient), so the data
obeys the same validation and business rules the UI does. Demo accounts all use
the password below; emails end in @example.com and are listed at the end.
"""

import argparse
import os
import sys
from pathlib import Path

# Make `app` importable when run as `python scripts/seed.py` from backend/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Seeding signs up many users quickly; the /auth rate limits would block it.
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

from fastapi.testclient import TestClient  # noqa: E402

from app import routes  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models.application import Application  # noqa: E402
from app.models.contract import Contract  # noqa: E402
from app.models.job import Job  # noqa: E402
from app.models.mentorship import Mentorship  # noqa: E402
from app.models.message import Message  # noqa: E402
from app.models.payment import Payment  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.auth import create_email_verify_token  # noqa: E402
from app.services.email import RecordingEmailSender  # noqa: E402

PASSWORD = "demo-pass-2026"
DOMAIN = "example.com"

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

USERS = [
    # key, first, last, type, city, country, visa, skills, languages, mentor, bio
    (
        "jihoon",
        "Jihoon",
        "Park",
        "founder",
        "Vancouver",
        "CA",
        "PR",
        ["Python", "Fintech", "Hiring"],
        ["Korean", "English"],
        False,
        "Co-founder of Hanmaeum Labs — cross-border payroll for small teams. Ex-Toss.",
    ),
    (
        "grace",
        "Grace",
        "Choi",
        "founder",
        "Toronto",
        "CA",
        "Citizen",
        ["Product", "Marketplaces"],
        ["English", "Korean"],
        True,
        "Building Maple & Kimchi, a marketplace for Korean grocers in the GTA. Happy to mentor first-time founders.",
    ),
    (
        "daniel",
        "Daniel",
        "Lee",
        "founder",
        "Toronto",
        "CA",
        "Citizen",
        ["ML", "Go", "Leadership"],
        ["English", "Korean"],
        False,
        "CTO at Northbridge AI. Half the team is in Seoul, half in Toronto.",
    ),
    (
        "minseo",
        "Minseo",
        "Kang",
        "engineer",
        "Seoul",
        "KR",
        "None yet",
        ["Python", "FastAPI", "Postgres", "AWS"],
        ["Korean", "English"],
        False,
        "Backend engineer at a Seoul fintech, 5 years. Looking for a Canadian team that sponsors.",
    ),
    (
        "yuna",
        "Yuna",
        "Oh",
        "iec_worker",
        "Vancouver",
        "CA",
        "IEC",
        ["React", "TypeScript", "Tailwind"],
        ["Korean", "English"],
        False,
        "Arrived in Vancouver in May on an IEC permit. Frontend dev, 3 years at a Pangyo startup.",
    ),
    (
        "hyunwoo",
        "Hyunwoo",
        "Shin",
        "engineer",
        "Toronto",
        "CA",
        "PR",
        ["Go", "Kubernetes", "Terraform"],
        ["Korean", "English"],
        True,
        "Platform engineer in Toronto since 2019. Came on IEC, now PR — ask me how.",
    ),
    (
        "seojin",
        "Seojin",
        "Lim",
        "immigrant",
        "Calgary",
        "CA",
        "PR",
        ["Java", "Spring", "Postgres"],
        ["Korean", "English"],
        True,
        "Landed in Calgary last year. 8 years of Java at Samsung SDS. Mentoring newcomers on the job hunt.",
    ),
    (
        "eunji",
        "Eunji",
        "Moon",
        "iec_worker",
        "Toronto",
        "CA",
        "IEC",
        ["SQL", "Python", "Tableau"],
        ["Korean", "English"],
        False,
        "Data analyst on a working holiday, open to part-time while I settle in.",
    ),
    (
        "taeyang",
        "Taeyang",
        "Kwon",
        "engineer",
        "Busan",
        "KR",
        "None yet",
        ["Flutter", "Dart", "Firebase"],
        ["Korean"],
        False,
        "Mobile developer in Busan. Remote-first, would relocate for the right team.",
    ),
    (
        "sarah",
        "Sarah",
        "Kim",
        "engineer",
        "Vancouver",
        "CA",
        "Citizen",
        ["Figma", "Design systems", "React"],
        ["English", "Korean"],
        True,
        "Product designer, born in Vancouver. Mentoring Korean designers breaking into North American teams.",
    ),
]

JOBS = [
    # key, founder, title, company, description, min, max, cur, skills, level, type, city, country, remote, sponsor, iec
    (
        "be_senior",
        "jihoon",
        "Senior Backend Engineer",
        "Hanmaeum Labs",
        "Own the payroll engine (FastAPI + Postgres). You'll work with a Seoul-based team and ship to Canadian SMBs. We sponsor and we've done IEC → PR before.",
        11000000,
        14000000,
        "CAD",
        ["Python", "FastAPI", "Postgres"],
        "senior",
        "full_time",
        "Vancouver",
        "CA",
        True,
        True,
        True,
    ),
    (
        "fe_react",
        "jihoon",
        "Frontend Engineer (React)",
        "Hanmaeum Labs",
        "React + TypeScript on a small, fast team. IEC holders welcome — two of us started that way.",
        8500000,
        10500000,
        "CAD",
        ["React", "TypeScript"],
        "mid",
        "full_time",
        "Vancouver",
        "CA",
        True,
        False,
        True,
    ),
    (
        "mobile_flutter",
        "jihoon",
        "Mobile Engineer (Flutter, contract)",
        "Hanmaeum Labs",
        "6-month contract to ship our first mobile app. Fully remote, Korea or Canada time zones.",
        6000,
        8000,
        "CAD",
        ["Flutter", "Dart"],
        "mid",
        "contract",
        None,
        None,
        True,
        False,
        False,
    ),
    (
        "fullstack",
        "grace",
        "Full-stack Developer",
        "Maple & Kimchi",
        "Next feature: grocer onboarding in Korean and English. Node or Python, your call. Hybrid in Toronto.",
        9000000,
        11500000,
        "CAD",
        ["TypeScript", "Postgres", "Korean"],
        "mid",
        "full_time",
        "Toronto",
        "CA",
        False,
        True,
        True,
    ),
    (
        "data_pt",
        "grace",
        "Part-time Data Analyst",
        "Maple & Kimchi",
        "15–20 hrs/week building our sales dashboards. Perfect for someone settling in on a working holiday.",
        3200,
        4000,
        "CAD",
        ["SQL", "Python", "Tableau"],
        "junior",
        "part_time",
        "Toronto",
        "CA",
        True,
        False,
        True,
    ),
    (
        "ml_seoul",
        "daniel",
        "ML Engineer (Seoul-based)",
        "Northbridge AI",
        "Join the Seoul half of our team. Korean employment contract with a Canadian company — we've got the template.",
        7000000000,
        9500000000,
        "KRW",
        ["Python", "PyTorch", "MLOps"],
        "senior",
        "full_time",
        "Seoul",
        "KR",
        True,
        False,
        False,
    ),
    (
        "devops",
        "daniel",
        "DevOps Engineer",
        "Northbridge AI",
        "Kubernetes on GCP across two regions. Toronto office, sponsorship available for the right person.",
        10000000,
        13000000,
        "CAD",
        ["Kubernetes", "Terraform", "Go"],
        "senior",
        "full_time",
        "Toronto",
        "CA",
        False,
        True,
        False,
    ),
]

# applicant, job, cover note, status set by the founder afterwards (None = applied)
APPLICATIONS = [
    (
        "minseo",
        "be_senior",
        "5 years of FastAPI/Postgres at a Seoul fintech. Sponsorship is the deciding factor for me.",
        "interviewing",
    ),
    (
        "minseo",
        "ml_seoul",
        "Interested in staying in Seoul while working with a Canadian team.",
        "reviewing",
    ),
    (
        "yuna",
        "fe_react",
        "IEC holder in Vancouver since May, React/TS for 3 years. Available immediately.",
        "offered",
    ),
    ("yuna", "fullstack", "Happy to do hybrid if Toronto works out.", "rejected"),
    (
        "hyunwoo",
        "devops",
        "Platform eng in Toronto, PR holder. Ran multi-region GKE at my last job.",
        "reviewing",
    ),
    (
        "eunji",
        "data_pt",
        "Data analyst on IEC, looking for exactly this kind of part-time role.",
        "hired",
    ),
    (
        "taeyang",
        "mobile_flutter",
        "Shipped two Flutter apps to 100k+ users. Remote from Busan works well for me.",
        None,
    ),
    (
        "seojin",
        "fullstack",
        "Java/Spring mostly, but I've shipped TypeScript too. Based in Calgary, would relocate.",
        None,
    ),
]

# founder, applicant, job, template, terms, final state: draft | pending | signed
CONTRACTS = [
    (
        "grace",
        "eunji",
        "data_pt",
        "part_time_gig",
        {
            "hourly_rate": 3500,
            "currency": "CAD",
            "start_date": "2026-10-01",
            "hours_per_week": 18,
        },
        "signed",
    ),
    (
        "jihoon",
        "yuna",
        "fe_react",
        "full_time_domestic",
        {"salary": 9500000, "currency": "CAD", "start_date": "2026-11-02"},
        "pending",
    ),
    (
        "daniel",
        "minseo",
        "ml_seoul",
        "korea_engineer_canada_co",
        {
            "salary": 8000000000,
            "currency": "KRW",
            "start_date": "2027-01-04",
            "work_location_country": "KR",
            "payment_schedule": "monthly",
        },
        "draft",
    ),
]

# mentee, mentor, notes, final state: requested | active | completed | declined
MENTORSHIPS = [
    (
        "yuna",
        "hyunwoo",
        "You went IEC → PR — I'd love to hear how you handled the timeline.",
        "active",
    ),
    (
        "eunji",
        "seojin",
        "Trying to figure out whether to stay in data or move toward engineering.",
        "requested",
    ),
    (
        "minseo",
        "sarah",
        "How do North American teams evaluate portfolios from Korea?",
        "completed",
    ),
    ("taeyang", "hyunwoo", "Looking for platform advice.", "declined"),
]

# sender, recipient, body
MESSAGES = [
    (
        "minseo",
        "jihoon",
        "Hi Jihoon — thanks for moving me to the interview stage. Does Thursday 9am KST work?",
    ),
    (
        "jihoon",
        "minseo",
        "Thursday works. It'll be me and our Seoul lead. We'll walk through the payroll engine.",
    ),
    ("minseo", "jihoon", "Perfect, see you then."),
    (
        "grace",
        "yuna",
        "Yuna, we went with a Toronto-based candidate for full-stack, but your React work was strong. Keep an eye on us.",
    ),
    ("yuna", "grace", "Appreciate you telling me directly. Will do!"),
    ("eunji", "seojin", "Sent you a mentorship request — would love 30 min sometime."),
    (
        "hyunwoo",
        "yuna",
        "Saw your request. Short version: apply for PR the week your one-year mark hits. Let's talk details.",
    ),
]

# sender, recipient, amount(cents), currency, type, notes, final: pending | cancelled
PAYMENTS = [
    (
        "grace",
        "eunji",
        140000,
        "CAD",
        "contract_payment",
        "October — first 40 hours",
        "pending",
    ),
    (
        "grace",
        "eunji",
        35000,
        "CAD",
        "contract_payment",
        "Duplicate — cancelled",
        "cancelled",
    ),
    (
        "daniel",
        "minseo",
        500000,
        "CAD",
        "contract_payment",
        "Signing bonus (recorded, pays out via Wise later)",
        "pending",
    ),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def email_for(key: str) -> str:
    return f"{key}@{DOMAIN}"


def ok(resp, expected):
    if resp.status_code != expected:
        raise SystemExit(
            f"{resp.request.method} {resp.request.url} -> {resp.status_code}: {resp.text}"
        )
    return resp.json() if resp.content else None


def reset_demo_rows(demo_emails):
    """Delete demo rows in FK order. Only rows that reference demo users are touched."""
    db = SessionLocal()
    try:
        ids = [u.id for u in db.query(User).filter(User.email.in_(demo_emails)).all()]
        if not ids:
            print("No demo rows to remove.")
            return
        job_ids = [j.id for j in db.query(Job).filter(Job.creator_id.in_(ids)).all()]
        app_q = db.query(Application).filter(
            (Application.user_id.in_(ids)) | (Application.job_id.in_(job_ids))
        )
        app_ids = [a.id for a in app_q.all()]
        db.query(Message).filter(
            (Message.sender_id.in_(ids)) | (Message.recipient_id.in_(ids))
        ).delete(synchronize_session=False)
        db.query(Payment).filter(
            (Payment.from_user_id.in_(ids)) | (Payment.to_user_id.in_(ids))
        ).delete(synchronize_session=False)
        db.query(Mentorship).filter(
            (Mentorship.mentor_id.in_(ids)) | (Mentorship.mentee_id.in_(ids))
        ).delete(synchronize_session=False)
        if app_ids:
            db.query(Contract).filter(Contract.application_id.in_(app_ids)).delete(
                synchronize_session=False
            )
        app_q.delete(synchronize_session=False)
        if job_ids:
            db.query(Job).filter(Job.id.in_(job_ids)).delete(synchronize_session=False)
        db.query(User).filter(User.id.in_(ids)).delete(synchronize_session=False)
        db.commit()
        print(f"Removed demo data for {len(ids)} users.")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--reset", action="store_true", help="remove existing demo rows first"
    )
    parser.add_argument(
        "--allow-production",
        action="store_true",
        help="required when ENVIRONMENT=production",
    )
    args = parser.parse_args()

    settings = get_settings()
    if settings.ENVIRONMENT == "production" and not args.allow_production:
        raise SystemExit(
            "Refusing to seed a production database without --allow-production."
        )

    demo_emails = [email_for(u[0]) for u in USERS]
    if args.reset:
        reset_demo_rows(demo_emails)

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email.in_(demo_emails)).count():
            raise SystemExit(
                "Demo data already present. Re-run with --reset to recreate it."
            )
    finally:
        db.close()

    # Don't spam the console with verification emails while seeding.
    routes.auth.get_email_sender = lambda: RecordingEmailSender()  # type: ignore[attr-defined]

    client = TestClient(app, base_url="http://localhost")
    headers: dict[str, dict] = {}
    user_ids: dict[str, int] = {}

    # Users: sign up, verify email, fill in profile.
    for (
        key,
        first,
        last,
        utype,
        city,
        country,
        visa,
        skills,
        langs,
        mentor,
        bio,
    ) in USERS:
        created = ok(
            client.post(
                "/api/auth/signup",
                json={
                    "email": email_for(key),
                    "password": PASSWORD,
                    "first_name": first,
                    "last_name": last,
                    "user_type": utype,
                    "country": country,
                    "city": city,
                },
            ),
            201,
        )
        user_ids[key] = created["id"]
        tokens = ok(
            client.post(
                "/api/auth/login", json={"email": email_for(key), "password": PASSWORD}
            ),
            200,
        )
        headers[key] = {"Authorization": f"Bearer {tokens['access_token']}"}
        ok(
            client.post(
                "/api/auth/verify-email",
                json={"token": create_email_verify_token(created["id"])},
            ),
            200,
        )
        ok(
            client.put(
                "/api/profile/me",
                headers=headers[key],
                json={
                    "bio": bio,
                    "skills": skills,
                    "languages": langs,
                    "visa_status": visa,
                    "mentor_available": mentor,
                },
            ),
            200,
        )
    print(f"users: {len(USERS)}")

    # Jobs
    job_ids: dict[str, int] = {}
    for (
        key,
        founder,
        title,
        company,
        desc,
        lo,
        hi,
        cur,
        skills,
        level,
        jtype,
        city,
        country,
        remote,
        sponsor,
        iec,
    ) in JOBS:
        job = ok(
            client.post(
                "/api/jobs",
                headers=headers[founder],
                json={
                    "title": title,
                    "company_name": company,
                    "description": desc,
                    "salary_min": lo,
                    "salary_max": hi,
                    "salary_currency": cur,
                    "skills": skills,
                    "experience_level": level,
                    "job_type": jtype,
                    "location_city": city,
                    "location_country": country,
                    "remote_ok": remote,
                    "visa_sponsorship": sponsor,
                    "iec_friendly": iec,
                },
            ),
            201,
        )
        job_ids[key] = job["id"]
    print(f"jobs: {len(JOBS)}")

    # Applications (+ founder-side status updates)
    app_ids: dict[tuple, int] = {}
    founder_of = {j[0]: j[1] for j in JOBS}
    for applicant, job_key, note, status in APPLICATIONS:
        application = ok(
            client.post(
                "/api/applications",
                headers=headers[applicant],
                json={"job_id": job_ids[job_key], "cover_note": note},
            ),
            201,
        )
        app_ids[(applicant, job_key)] = application["id"]
        if status:
            ok(
                client.put(
                    f"/api/applications/{application['id']}",
                    headers=headers[founder_of[job_key]],
                    json={"status": status},
                ),
                200,
            )
    print(f"applications: {len(APPLICATIONS)}")

    # Contracts
    for founder, applicant, job_key, template, terms, state in CONTRACTS:
        contract = ok(
            client.post(
                "/api/contracts",
                headers=headers[founder],
                json={
                    "application_id": app_ids[(applicant, job_key)],
                    "template_type": template,
                    "terms": terms,
                },
            ),
            201,
        )
        if state in ("pending", "signed"):
            ok(
                client.post(
                    f"/api/contracts/{contract['id']}/send", headers=headers[founder]
                ),
                200,
            )
        if state == "signed":
            ok(
                client.post(
                    f"/api/contracts/{contract['id']}/sign", headers=headers[applicant]
                ),
                200,
            )
    print(f"contracts: {len(CONTRACTS)}")

    # Mentorships
    for mentee, mentor, notes, state in MENTORSHIPS:
        m = ok(
            client.post(
                "/api/mentorships",
                headers=headers[mentee],
                json={"mentor_id": user_ids[mentor], "notes": notes},
            ),
            201,
        )
        if state in ("active", "completed"):
            ok(
                client.post(
                    f"/api/mentorships/{m['id']}/accept", headers=headers[mentor]
                ),
                200,
            )
        if state == "completed":
            ok(
                client.post(
                    f"/api/mentorships/{m['id']}/complete", headers=headers[mentee]
                ),
                200,
            )
        if state == "declined":
            ok(
                client.post(
                    f"/api/mentorships/{m['id']}/decline", headers=headers[mentor]
                ),
                200,
            )
    print(f"mentorships: {len(MENTORSHIPS)}")

    # Messages (in order, so threads read naturally)
    for sender, recipient, body in MESSAGES:
        ok(
            client.post(
                "/api/messages",
                headers=headers[sender],
                json={"recipient_id": user_ids[recipient], "body": body},
            ),
            201,
        )
    print(f"messages: {len(MESSAGES)}")

    # Payments (records only — nothing moves)
    for sender, recipient, amount, cur, ptype, notes, state in PAYMENTS:
        p = ok(
            client.post(
                "/api/payments",
                headers=headers[sender],
                json={
                    "to_user_id": user_ids[recipient],
                    "amount": amount,
                    "currency": cur,
                    "payment_type": ptype,
                    "notes": notes,
                },
            ),
            201,
        )
        if state == "cancelled":
            ok(
                client.post(f"/api/payments/{p['id']}/cancel", headers=headers[sender]),
                200,
            )
    print(f"payments: {len(PAYMENTS)}")

    print("\nDemo accounts (password for all: %s)" % PASSWORD)
    print(f"  {'email':<24} {'role':<11} {'name':<16} where")
    for key, first, last, utype, city, country, *_ in USERS:
        print(
            f"  {email_for(key):<24} {utype:<11} {first + ' ' + last:<16} {city}, {country}"
        )
    print(
        "\nTip: log in as jihoon@example.com to see applicants, a pending contract and a live thread;"
    )
    print(
        "     as yuna@example.com to see the talent side (offer, contract to sign, mentor)."
    )


if __name__ == "__main__":
    main()
