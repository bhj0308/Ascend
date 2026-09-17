# Database Schema

PostgreSQL, managed via SQLAlchemy models (`backend/app/models/`, the source of truth) and
Alembic migrations (`backend/migrations/`).

## Conventions

- **Every table** inherits `id` (int PK), `created_at`, `updated_at` from `models/base.py`.
  Timestamps are **timezone-aware UTC** (`timestamptz`), set with `_utcnow()` — never
  `datetime.utcnow()`.
- **Money** is an integer number of cents (or the currency's smallest unit) in a `bigint`
  column, next to an ISO 4217 currency code. `int4` overflows at ₩21.5M in cents.
- **Enums** are Postgres enum types. SQLAlchemy stores the Python member **name**
  (`'FOUNDER'`), while the API returns the value (`'founder'`). Use names in raw SQL.
- **Dates without a time** (visa expiry, deadlines, contract start dates) are ISO date strings.
- **Users are never hard-deleted.** Account deletion anonymizes the row (see below) so
  contracts, payments, and messages stay intact for the other party.

## Entity-relationship overview

```
User ──< Job (creator_id)
User ──< Application (user_id)
Job  ──< Application (job_id)
Application ──1 Contract (application_id)
User ──< Payment (from_user_id / to_user_id)
User ──< Mentorship (mentor_id / mentee_id)
User ──< Message (sender_id / recipient_id)
Job  ──< Message (job_id, optional context)
```

## Tables

### `users`
| Column | Type | Notes |
|---|---|---|
| email | varchar(255), unique | replaced with `deleted-<id>@deleted.invalid` on deletion |
| password_hash | varchar, nullable | bcrypt; null for OAuth-only or deleted accounts; never serialized |
| first_name / last_name | varchar(100) | |
| avatar_url | varchar(500) | not used by the UI yet |
| bio | text | |
| user_type | enum | `founder`, `engineer`, `iec_worker`, `immigrant`, `admin` |
| status | enum | `active`, `inactive` (deleted), `suspended`; only `active` users can authenticate |
| country | varchar(2) | ISO country code |
| city | varchar(100) | |
| phone | varchar(20) | never shown on public profiles |
| google_id / github_id | varchar, unique, nullable | reserved for OAuth (not wired) |
| skills / languages | JSON array | |
| timezone | varchar(50) | |
| visa_status | varchar(100) | free text, e.g. "IEC", "PR", "Work Permit" |
| visa_expiry | ISO date string | |
| email_verified | bool | set by `POST /auth/verify-email` |
| two_factor_enabled | bool | reserved, unused |
| mentor_available | bool, not null, default false | opt-in to the mentor directory |

### `jobs`
| Column | Type | Notes |
|---|---|---|
| creator_id | int, FK → users.id | |
| title / description | varchar / text | |
| company_name | varchar | |
| salary_min / salary_max | **bigint** (cents) | |
| salary_currency | varchar(3) | default `CAD` |
| skills | JSON array | |
| experience_level | varchar | |
| job_type | enum | `full_time`, `part_time`, `contract`, `internship` |
| status | enum | `draft`, `open`, `closed`, `filled`; account deletion closes open jobs |
| location_country / location_city | varchar(2) / varchar(100) | |
| remote_ok / visa_sponsorship / iec_friendly | bool | the board's filters |
| positions_available | int | |
| application_deadline | ISO date string | |

### `applications`
| Column | Type | Notes |
|---|---|---|
| job_id | int, FK → jobs.id | |
| user_id | int, FK → users.id | |
| status | enum | `applied`, `reviewing`, `interviewing`, `offered`, `rejected`, `hired`, `withdrawn` |
| cover_note | text | |
| notes | text | hiring-side only |

One application per `(job_id, user_id)` — enforced in the route, not by a DB constraint.

### `contracts`
| Column | Type | Notes |
|---|---|---|
| application_id | int, FK → applications.id | one contract per application (enforced in the route) |
| template_type | enum | `korea_engineer_canada_co`, `canada_engineer_korea_co`, `remote_contractor`, `full_time_domestic`, `part_time_gig` |
| status | enum | `draft` → `pending_signature` → `signed`; `cancelled` from any non-signed state |
| terms | JSON | validated per template in `services/contracts.py` (`salary` or `hourly_rate` in cents, `currency`, `start_date`, plus template-specific fields) |
| docusign_envelope_id | varchar | reserved for `ENABLE_DOCUSIGN` |
| signed_at | timestamptz | set when the applicant acknowledges |

### `payments`
Ledger only — no money moves.

| Column | Type | Notes |
|---|---|---|
| from_user_id | int, FK → users.id | always the authenticated sender |
| to_user_id | int, FK → users.id, nullable | null for off-platform recipients |
| amount | **bigint** (cents) | > 0 |
| currency | varchar(3) | |
| payment_type | enum | `salary`, `contract_payment`, `remittance` |
| status | enum | `pending`, `processing`, `complete`, `failed`, `cancelled` (only `pending`/`cancelled` reachable today) |
| wise_transaction_id | varchar | reserved for `ENABLE_WISE_PAYMENTS` |
| recipient_name / recipient_email | varchar | off-platform recipients |
| notes | varchar(500) | |

### `mentorships`
| Column | Type | Notes |
|---|---|---|
| mentor_id / mentee_id | int, FK → users.id | requester is the mentee |
| status | enum | `requested` → `active` / `declined`; `active` → `completed` |
| notes | text | |

At most one `requested`/`active` mentorship per pair (either direction), enforced in the route.

### `messages`
| Column | Type | Notes |
|---|---|---|
| sender_id / recipient_id | int, FK → users.id | |
| job_id | int, FK → jobs.id, nullable | conversation context |
| body | text | non-blank |
| read | bool | set when the recipient opens the thread |

## Account deletion (anonymization)

`DELETE /profile/me` keeps the row but: clears names, bio, phone, avatar, location, skills,
languages, timezone, visa fields, and OAuth ids; resets `email_verified`; sets email to `deleted-<id>@deleted.invalid`; nulls `password_hash`; sets
`status = inactive` and `mentor_available = false`; closes the user's open jobs. Counterparties
then see "User #<id>". Existing tokens stop working because `get_current_user` requires `active`.

## Migration history

| Revision | Change |
|---|---|
| `22a05cdfdeae` | Initial schema (all tables and enums) |
| `9131e64c9492` | Timestamps → `timestamptz` |
| `c51198653bfa` | `users.mentor_available` |
| `70317845a84a` | `salary_min`, `salary_max`, `amount` → `bigint` |

## Migrations

```bash
cd backend
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
alembic downgrade -1
```

Review every autogenerated file. Autogenerate does **not** drop new Postgres enum types in
`downgrade()` — add `op.execute("DROP TYPE IF EXISTS <name>")` or the next `upgrade` fails with
`DuplicateObject`. Production runs `alembic upgrade head` on every API start, and a Render rollback
does not downgrade the database, so keep migrations additive.
