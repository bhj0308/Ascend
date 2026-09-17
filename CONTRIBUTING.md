# Contributing to Ascend

## Workflow

1. Branch off `main`: `git checkout -b feature/short-description`
2. Make focused commits (see commit format below)
3. Push and open a pull request describing what changed and why
4. Get it reviewed, address feedback, merge

## Commit message format

```
<type>: <short description>

Types:
  feat     New feature
  fix      Bug fix
  docs     Documentation only
  style    Formatting, no logic change
  refactor Code change that isn't a fix or feature
  test     Adding or updating tests
  chore    Dependencies, tooling, config
```

## Code style

- **Backend (Python 3.13):** `black` + `isort`, type hints on public functions. CI runs the
  check on `app/` and `tests/`.
  ```bash
  cd backend
  black app/ tests/ scripts/ && isort app/ tests/ scripts/
  ```
- **Frontend (TypeScript/React):** functional components with hooks; match the Tailwind utility
  style of neighbouring pages. The gate is the type-check + build:
  ```bash
  cd frontend
  npm run build
  ```
  ESLint and Vitest are installed but **not configured yet** (no `eslint.config.js`, no test
  files). Setting them up is welcome as its own PR.

## Tests

- **Backend:** `pytest` against a real Postgres database (`ascend_test`; see
  [docs/SETUP.md](docs/SETUP.md#5-tests)). Tests live in `backend/tests/routes/test_<resource>.py`
  and use the fixtures in `tests/conftest.py` (`client`, `founder`, `applicant`, `other_user`).
  ```bash
  cd backend
  pytest -q
  ```
  Every new route ships with tests for the happy path **and** its 401/403/404/400 boundaries —
  `tests/routes/test_contracts.py` is the reference.
- **Manual end-to-end:** `python scripts/seed.py` gives you ten accounts with realistic data to
  click through.

## Changing the database

1. Edit `backend/app/models/`.
2. `alembic revision --autogenerate -m "..."`, review the file, and add
   `op.execute("DROP TYPE IF EXISTS <enum>")` to `downgrade()` for any new enum.
3. Prove `upgrade → downgrade → upgrade` locally (or run `/migrate` in Claude Code).
4. Keep migrations additive — production applies them at startup and rollbacks don't downgrade.
5. Update `docs/DATABASE.md` (tables + migration history).

## Adding a new backend resource

All current models already have routes, so a new resource usually means a new model too.
Follow `routes/contracts.py` + `tests/routes/test_contracts.py`:

1. Model in `models/<resource>.py` (inherit `BaseModel`; money as `BigInteger` cents), export it
   from `models/__init__.py`, then migrate (above)
2. Schemas in `schemas/<resource>.py` — never return `User` emails for other users
   (use `PublicUserResponse`)
3. Router in `routes/<resource>.py`, registered in `main.py` with
   `app.include_router(<resource>.router, prefix="/api/<resource>", tags=[...])`
4. Tests in `tests/routes/test_<resource>.py`
5. Document every endpoint and error case in `docs/API.md`

In Claude Code, `/add-resource` walks through this and `/feature` runs backend, frontend, and
reviewer agents in parallel.

## Adding a new frontend page

1. Create the component in `src/pages/<PageName>.tsx`
2. Add API calls to the relevant file in `src/services/` (or create one)
3. Add or extend types in `src/types/<resource>.ts`
4. Register the route in `src/App.tsx`
5. Link to it from `src/components/Navbar.tsx` if it should be discoverable
6. Use TanStack Query for server data and show the backend's `detail` on errors

## Sensitive content (contracts, tax/visa guides)

Any content in the knowledge base or contract templates that touches
employment law, tax, or immigration must be reviewed by a qualified
professional (accountant/lawyer) before shipping to production — flag this
explicitly in your PR description. See `docs/PRODUCT.html` for the current
plan around a Korean-Canadian accountant partnership for this review.

## Questions

Open a GitHub issue or discussion — this is an early-stage project and we'd
rather over-communicate on direction than have duplicated or conflicting work.
