# API Reference

Base URL (local dev): `http://localhost:8000/api`

Interactive docs (Swagger UI): `http://localhost:8000/docs`
Interactive docs (ReDoc): `http://localhost:8000/redoc`

Authenticated endpoints expect `Authorization: Bearer <access_token>`.

## Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/signup` | none | Register with email/password. Returns the created user. |
| POST | `/auth/login` | none | Exchange email/password for access + refresh JWTs. |
| GET | `/auth/me` | required | Get the current authenticated user. |

**POST `/auth/signup`**
```json
{
  "email": "jane@example.com",
  "password": "hunter22",
  "first_name": "Jane",
  "last_name": "Kim",
  "user_type": "engineer",
  "country": "KR",
  "city": "Seoul"
}
```

**POST `/auth/login`**
```json
{ "email": "jane@example.com", "password": "hunter22" }
```
Response:
```json
{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }
```

## Profile

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/profile/me` | required | Full profile of the current user. |
| PUT | `/profile/me` | required | Update editable profile fields. |
| GET | `/profile/{user_id}` | none | View another user's public profile. |

## Jobs

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/jobs` | none | Browse open jobs. Query params: `skills`, `location_country`, `remote_ok`, `visa_sponsorship`, `iec_friendly`. |
| POST | `/jobs` | required | Create a job posting (any authenticated user can post; UI restricts to founders). |
| GET | `/jobs/{job_id}` | none | Get a single job. |
| PUT | `/jobs/{job_id}` | required (creator only) | Update a job posting. |
| DELETE | `/jobs/{job_id}` | required (creator only) | Delete a job posting. |

## Applications

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/applications` | required | Apply to a job. One application per user per job. |
| GET | `/applications/me` | required | List the current user's applications. |
| GET | `/applications/job/{job_id}` | required (job creator only) | List applications for a job. |
| PUT | `/applications/{application_id}` | required (job creator only) | Update application status/notes. |

## Not yet implemented (see docs/PRODUCT.html for roadmap)

- `POST /contracts` — generate a contract from a template
- `PUT /contracts/{id}` — e-signature webhook/status update
- `POST /payments` — initiate a Wise transfer
- `GET /payments/me/history` — payment history
- `GET /mentorship/available_mentors`
- `POST /mentorship`
- `GET /knowledge/guides`
- `GET /messages` / `POST /messages`

These are stubbed in the product plan (`docs/PRODUCT.html`) under Phase 2–3
and will get their own `routes/*.py` + `schemas/*.py` + `models/*.py` (mostly
already scaffolded for contracts/payments/mentorship/messages) as those
phases start.
