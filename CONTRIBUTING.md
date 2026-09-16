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

- **Backend (Python):** `black` for formatting, `isort` for import order,
  type hints on all public functions.
  ```bash
  cd backend
  black app/
  isort app/
  ```
- **Frontend (TypeScript/React):** ESLint + Prettier defaults. Functional
  components with hooks; no class components.
  ```bash
  cd frontend
  npm run lint
  ```

## Tests

- **Backend:** `pytest` — put tests in `backend/tests/`, mirroring the
  `app/` structure (e.g. `tests/routes/test_jobs.py`).
  ```bash
  cd backend
  pytest
  ```
- **Frontend:** `vitest` — colocate `*.test.tsx` next to the component it
  tests.
  ```bash
  cd frontend
  npm run test
  ```

New routes/services should ship with at least a happy-path test before
merging.

## Adding a new backend resource (e.g. `mentorship`)

The models, schemas, and services for `Contract`, `Payment`, `Mentorship`,
and `Message` already exist in `backend/app/models/` — most of Phase 2/3 work
is writing the `routes/*.py` file and wiring it into `main.py`. Follow the
existing pattern in `routes/jobs.py` / `routes/applications.py`:

1. Add Pydantic schemas in `schemas/<resource>.py` if not already present
2. Add a router in `routes/<resource>.py` with CRUD endpoints
3. Register it in `main.py`: `app.include_router(<resource>.router, prefix="/api/<resource>", tags=[...])`
4. Add tests in `tests/routes/test_<resource>.py`
5. Update `docs/API.md`

## Adding a new frontend page

1. Create the component in `src/pages/<PageName>.tsx`
2. Add API calls to the relevant file in `src/services/` (or create one)
3. Register the route in `src/App.tsx`
4. Link to it from `src/components/Navbar.tsx` if it should be discoverable

## Sensitive content (contracts, tax/visa guides)

Any content in the knowledge base or contract templates that touches
employment law, tax, or immigration must be reviewed by a qualified
professional (accountant/lawyer) before shipping to production — flag this
explicitly in your PR description. See `docs/PRODUCT.html` for the current
plan around a Korean-Canadian accountant partnership for this review.

## Questions

Open a GitHub issue or discussion — this is an early-stage project and we'd
rather over-communicate on direction than have duplicated or conflicting work.
