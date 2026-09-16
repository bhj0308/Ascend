# Ascend (repo folder: TalentFlow)

Two-sided tech-talent marketplace: Korean-Canadian founders hiring engineers
(Korea first, global later) + IEC working-holiday / immigrant talent finding
jobs in Canada, with contracts, compliance guides, and cross-border payments.
Product name is **Ascend**; the folder is still `TalentFlow`.

Keep this file short — it loads every session. Long workflows live in
`.claude/skills/`; design docs live in `docs/`.

## Layout
- `backend/` FastAPI + SQLAlchemy 2 + Alembic + Postgres. Entry: `app/main.py`.
  `models/` (ORM, source of truth) → `schemas/` (Pydantic) → `routes/` → `services/`.
- `frontend/` React 18 + TS + Vite + Tailwind. `src/pages/` routes, `src/services/` axios
  clients, `src/store/authStore.ts` (Zustand, client state only), `src/types/` mirrors backend schemas.
- `docs/` ARCHITECTURE, DATABASE, API, SETUP, PRODUCT.html (roadmap). Read only when needed.

## Status (Sept 2026)
- **Done, smoke-tested:** auth (signup/login/JWT), profiles, jobs CRUD + filters,
  applications + status pipeline, permission boundaries (401/403). 13 API routes.
- **Models exist but no routes yet:** Contract, Payment, Mentorship, Message.
  Phase 2/3 work = write `routes/<x>.py` + register in `main.py` (pattern: `routes/jobs.py`).
- Frontend: Home, Jobs, JobDetail, JobNew, Login, Signup, Profile, Guides (placeholder).

## Run / verify
```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload   # :8000, /docs
cd frontend && npm run dev                                                # :5173
cd frontend && npm run build                                              # tsc + vite, must pass
cd backend && black app/ migrations/env.py && isort app/ migrations/env.py  # must be clean
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
