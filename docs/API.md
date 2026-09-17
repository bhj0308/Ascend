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

## Contracts

Contract templates are convenience scaffolding, not legal advice — see
`app/services/contracts.py` for the "not legal advice" note and the
required-terms design (every template needs `salary` or `hourly_rate`,
`currency`, and `start_date`; some add cross-border fields).

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/contracts/templates` | required | List available contract templates and their required terms. |
| GET | `/contracts/me` | required | List contracts where the current user is the job creator (founder) or the applicant. |
| POST | `/contracts` | required (job creator only) | Generate a draft contract for an application from a template. 404 if application missing, 400 if it already has a contract or required terms are missing. |
| GET | `/contracts/{contract_id}` | required (founder or applicant only) | Get a single contract. |
| PUT | `/contracts/{contract_id}` | required (founder only) | Replace a draft contract's terms. 400 if not in `draft` status. |
| POST | `/contracts/{contract_id}/send` | required (founder only) | `draft` -> `pending_signature`. Manual transition only; DocuSign integration is behind the `ENABLE_DOCUSIGN` flag and not called here. |
| POST | `/contracts/{contract_id}/sign` | required (applicant only) | `pending_signature` -> `signed`, sets `signed_at`. This is an in-app acknowledgment, not a legal e-signature. |
| POST | `/contracts/{contract_id}/cancel` | required (founder only) | Any status except `signed` -> `cancelled`. |

## Payments

Payments are a **ledger only** in this version: recording a payment creates a
`pending` row (useful for history/tax records) but **no money moves**. Executing
a transfer is behind the `ENABLE_WISE_PAYMENTS` flag and not implemented yet.
Amounts are integer cents.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/payments` | required | Record a payment; sender = current user. Exactly one of `to_user_id` / `recipient_email` (400 otherwise); 400 if paying yourself; 404 if `to_user_id` doesn't exist; 422 if `amount <= 0` or `currency` isn't 3 letters. Creates `pending`. |
| GET | `/payments/me` | required | Payments where the current user is sender or recipient, newest first. |
| GET | `/payments/{payment_id}` | required (sender or recipient only) | Get a single payment. |
| POST | `/payments/{payment_id}/cancel` | required (sender only) | `pending` -> `cancelled`. 400 if not pending. |
| POST | `/payments/{payment_id}/execute` | required (sender only) | Always **501** in this version; status is never changed. 400 if not pending. |

## Mentorships

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/mentorships` | required | Request mentorship from `mentor_id`; requester becomes the mentee. 404 unknown mentor; 400 if requesting yourself or a `requested`/`active` mentorship already exists between the two users (either direction). Creates `requested`. |
| GET | `/mentorships/me` | required | Mentorships where the current user is mentor or mentee, newest first. |
| GET | `/mentorships/{mentorship_id}` | required (mentor or mentee only) | Get a single mentorship. |
| POST | `/mentorships/{mentorship_id}/accept` | required (mentor only) | `requested` -> `active`. 400 if not requested. |
| POST | `/mentorships/{mentorship_id}/decline` | required (mentor only) | `requested` -> `declined`. 400 if not requested. |
| POST | `/mentorships/{mentorship_id}/complete` | required (mentor or mentee) | `active` -> `completed`. 400 if not active. |

## Messages

Plain HTTP; clients poll. No websockets in this version.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/messages` | required | Send a message; sender = current user. 404 if `recipient_id` or optional `job_id` doesn't exist; 400 if sending to yourself or the body is empty/whitespace. |
| GET | `/messages/threads` | required | One summary per user you've exchanged messages with: `user_id`, `user_name`, `last_message_body`, `last_message_at`, `unread_count`; newest first. |
| GET | `/messages/with/{user_id}` | required | Full history with that user, oldest first. 404 if the user doesn't exist. Side effect: marks their unread messages to you as read. Any user may open an (empty) thread with any existing user. |

## Not yet implemented (see docs/PRODUCT.html for roadmap)

- `POST /payments/{payment_id}/execute` doing a real Wise transfer (`ENABLE_WISE_PAYMENTS`)
- `POST /contracts/{contract_id}/send` creating a DocuSign envelope (`ENABLE_DOCUSIGN`)
- A mentor directory (`GET /mentorships/mentors`) — needs a "mentor available" flag on `User` and a migration
- `GET /knowledge/guides` — knowledge base content
