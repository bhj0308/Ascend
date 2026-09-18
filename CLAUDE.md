# Ascend

Two-sided tech-talent marketplace: Korean-Canadian founders hiring engineers
(Korea first, global later) + IEC working-holiday / immigrant talent finding
jobs in Canada, with contracts, compliance guides, and cross-border payments.
Repo folder and product name are both **Ascend**.

Keep this file short — it loads every session. Long workflows live in
`.claude/skills/`; design docs live in `docs/`.

## Layout
- `backend/` FastAPI + SQLAlchemy 2 + Alembic + Postgres. Entry: `app/main.py`.
  `models/` (ORM, source of truth) → `schemas/` (Pydantic) → `routes/` → `services/`.
- `frontend/` React 18 + TS + Vite + Tailwind. `src/pages/` routes, `src/services/` axios
  clients, `src/store/authStore.ts` (Zustand, client state only), `src/types/` mirrors backend schemas.
- `docs/` ARCHITECTURE, DATABASE, API, SETUP, PRODUCT.html (roadmap). Read only when needed.

## Status (Sept 2026)
- **Done, tested:** auth, profiles, jobs CRUD + filters, applications pipeline, **contracts**
  (templates → draft → send → sign/cancel, typed terms), **payments** (ledger only — `execute`
  is 501 until Wise is wired), **mentorships** (request → accept/decline → complete),
  **messages** (threads + per-user history, mark-read on open, polling), token refresh,
  password reset + email verification, rate limiting on `/auth/*`, account deletion
  (anonymizing), mentor directory. 40 API paths.
  Every model has routes. `backend/tests/` is a real-Postgres pytest harness (`ascend_test`
  via `TEST_DATABASE_URL`, default `localhost:5433`) — 91 tests. Add to it; don't verify by hand. New resource pattern:
  `routes/contracts.py` + `tests/routes/test_contracts.py`.
- Frontend (25 routes): Landing `/` (KO/EN toggle, copy in `src/content/landing.ts`; animated hero,
  live open-roles marquee from `GET /jobs`, scroll reveals via `src/hooks/useReveal.ts`), Jobs, JobDetail, JobNew, JobApplicants (names → `/users/:id`),
  Contracts/ContractNew/ContractDetail (+ "Record payment" for founder), Payments/PaymentNew/
  PaymentDetail (ledger-only banner), Mentorships, Mentors `/mentors` (directory), PublicProfile `/users/:id` (request mentorship
  + message), Messages/MessageThread (polling 15s/5s), Login (+ forgot/reset password), Signup, VerifyEmail, Profile (editor, mentor toggle,
  delete account), Guides (placeholder),
  Terms/Privacy (drafts, marked). `App.tsx` `AuthBootstrap` restores the session on reload.
  Per-resource types live in `src/types/<resource>.ts`; shared `User`/`Job`/`Application` in `types/index.ts`.

## Run / verify
```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload   # :8000, /docs
cd frontend && npm run dev                                                # :5173
cd frontend && npm run build                                              # tsc + vite, must pass
cd backend && black app/ tests/ && isort app/ tests/                       # must be clean
cd backend && pytest -q                                                   # needs ascend_test DB
cd backend && python scripts/seed.py [--reset]                            # demo data via the real API
backend/scripts/seed_render.sh [--reset]                                   # same, against Render (URL in git-ignored backend/.env.render.local)
```
Deploy: `render.yaml` + `docs/DEPLOY.md` (Render blueprint, migrations at start, CI in `.github/`).
DB URL comes from `backend/.env` (gitignored; copy from `.env.example`). Full setup: `docs/SETUP.md`.

## Hard-won gotchas
- **Alembic autogenerate does not drop Postgres enum types in `downgrade()`.** After
  `alembic revision --autogenerate`, add `op.execute("DROP TYPE IF EXISTS <name>")` for
  every new enum, or `downgrade → upgrade` fails with DuplicateObject.
- SQLAlchemy `Enum` columns persist the Python member **name** (`'FOUNDER'`), not the
  value (`'founder'`). API JSON shows values. Never filter on values in raw SQL.
- Money is integer **cents** (`salary_min`, `amount`) + ISO currency code. No floats. Columns
  are `BigInteger`: KRW in cents overflows int32 at ₩21.5M (a seed run found this).
- Passwords: `bcrypt` directly (no passlib). Public `UserResponse` must never include `password_hash`.
- Python is 3.13 here; pin deps to versions with 3.13 wheels.
- `ENVIRONMENT=production` refuses to start with the default/short `SECRET_KEY`. `CORS_ORIGINS`
  and `ALLOWED_HOSTS` are comma-separated strings (`settings.cors_origins_list`).
- Access tokens last 30 min; `frontend/src/services/api.ts` refreshes once on 401 then retries.
  Refresh tokens are stateless (no revocation list).
- Timestamps are timezone-aware UTC (`DateTime(timezone=True)`, `_utcnow()` in `models/base.py`);
  never use `datetime.utcnow()`. Date-only strings (contract `*_date` terms) must be formatted
  with `frontend/src/utils/dates.ts::formatDateOnly`, not `new Date(str)` (off-by-one west of UTC).
- `display_name()` falls back to `User #<id>`, never the email/local-part.
- Emails: `services/email.py` — console sender logs a `===== EMAIL to … =====` block (the
  reset/verify link is one greppable line) until `SENDGRID_API_KEY` is set. Reset tokens embed a
  fingerprint of the current password hash, so they die when the password changes.
- Rate limits (`services/ratelimit.py`, slowapi, keyed on first `X-Forwarded-For`): tests set
  `RATE_LIMIT_ENABLED=false` in `conftest.py`; decorated routes need a `request: Request` param.
- Account deletion anonymizes (status `inactive`, email → `deleted-<id>@deleted.invalid`);
  `get_current_user` rejects non-active users. Never hard-delete users.
- Landing motion is Tailwind keyframes (`tailwind.config.js`) + `.reveal` in `styles/index.css`, all
  disabled under `prefers-reduced-motion`. Use `overflow-clip`, not `overflow-hidden`, on containers
  with bleeding decorations — `hidden` still scrolls programmatically (focus shifted the hero 96px).
- `GET /profile/{id}` returns `PublicUserResponse` — never email. Only `/profile/me` and
  `/auth/me` include it. Don't display emails as name fallbacks.

## Rules
- Never commit `.env`, `venv/`, `node_modules/`, `dist/`.
- Guides / contract templates touching tax, visa, or employment law are **not legal advice**
  and need professional review before production. Say so in the UI.
- Match existing style; no speculative abstractions. One route file per resource.
- Commit only when asked. Commits are authored by the user's own git identity.
