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
  **messages** (threads + per-user history, mark-read on open, polling). 34 API paths.
  Every model has routes. `backend/tests/` is a real-Postgres pytest harness (`ascend_test`
  DB on the `.env` host) — 56 tests. Add to it; don't verify by hand. New resource pattern:
  `routes/contracts.py` + `tests/routes/test_contracts.py`.
- Frontend (19 routes): Home, Jobs, JobDetail, JobNew, JobApplicants (names → `/users/:id`),
  Contracts/ContractNew/ContractDetail (+ "Record payment" for founder), Payments/PaymentNew/
  PaymentDetail (ledger-only banner), Mentorships, PublicProfile `/users/:id` (request mentorship
  + message), Messages/MessageThread (polling 15s/5s), Login, Signup, Profile, Guides (placeholder).
  Per-resource types live in `src/types/<resource>.ts`; shared `User`/`Job`/`Application` in `types/index.ts`.

## Run / verify
```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload   # :8000, /docs
cd frontend && npm run dev                                                # :5173
cd frontend && npm run build                                              # tsc + vite, must pass
cd backend && black app/ tests/ && isort app/ tests/                       # must be clean
cd backend && pytest -q                                                   # needs ascend_test DB
```
DB URL comes from `backend/.env` (gitignored; copy from `.env.example`). Full setup: `docs/SETUP.md`.

## Hard-won gotchas
- **Alembic autogenerate does not drop Postgres enum types in `downgrade()`.** After
  `alembic revision --autogenerate`, add `op.execute("DROP TYPE IF EXISTS <name>")` for
  every new enum, or `downgrade → upgrade` fails with DuplicateObject.
- SQLAlchemy `Enum` columns persist the Python member **name** (`'FOUNDER'`), not the
  value (`'founder'`). API JSON shows values. Never filter on values in raw SQL.
- Money is integer **cents** (`salary_min`, `amount`) + ISO currency code. No floats.
- Passwords: `bcrypt` directly (no passlib). Public `UserResponse` must never include `password_hash`.
- Python is 3.13 here; pin deps to versions with 3.13 wheels.

## Rules
- Never commit `.env`, `venv/`, `node_modules/`, `dist/`.
- Guides / contract templates touching tax, visa, or employment law are **not legal advice**
  and need professional review before production. Say so in the UI.
- Match existing style; no speculative abstractions. One route file per resource.
- Commit only when asked. Commits are authored by the user's own git identity.
