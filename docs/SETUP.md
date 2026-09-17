# Local Development Setup

## Prerequisites

- **Python 3.13** (dependencies are pinned to versions with 3.13 wheels)
- **Node.js 20** (what CI uses)
- **PostgreSQL 14+** running locally
- Redis is **not** needed — nothing uses it yet.

## 1. Databases

Two databases: one for the app, one the test suite creates and drops tables in.

```bash
createdb ascend_dev
createdb ascend_test
```

## 2. Backend

```bash
cd backend
python3.13 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set DATABASE_URL to your local Postgres, e.g.
#   postgresql://postgres:postgres@localhost:5432/ascend_dev

alembic upgrade head            # applies all migrations
uvicorn app.main:app --reload
```

API: http://localhost:8000 · Swagger: http://localhost:8000/docs · Health: http://localhost:8000/health

Defaults that matter locally:
- **Emails are printed to the uvicorn log**, not sent (no `SENDGRID_API_KEY`). Password-reset and
  verification links appear as one line inside an `===== EMAIL to … =====` block — copy it
  into the browser.
- **Rate limits are on** for `/auth/*` (e.g. signup 5/min per IP). If you hammer signup while
  testing, wait a minute or set `RATE_LIMIT_ENABLED=false` in `.env`.

## 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_URL=http://localhost:8000/api
npm run dev
```

App: http://localhost:5173. `VITE_API_URL` works with or without the trailing `/api`
(`services/api.ts` normalizes it).

## 4. Demo data

```bash
cd backend
python scripts/seed.py            # 10 accounts + jobs, applications, contracts, mentorships, messages, payments
python scripts/seed.py --reset    # delete the demo rows and recreate them
```

Every demo account uses the password `demo-pass-2026`; the script prints the list. It refuses
to run twice without `--reset`, and refuses `ENVIRONMENT=production` without `--allow-production`.

## 5. Tests

```bash
cd backend
pytest -q
```

The suite runs against real Postgres. It uses `TEST_DATABASE_URL`, defaulting to
`postgresql://postgres@localhost:5433/ascend_test` — if your Postgres is on 5432 or needs a
password, override it:

```bash
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ascend_test pytest -q
```

Tables are created at session start and dropped at the end, so never point this at `ascend_dev`.
Rate limiting is disabled for tests in `tests/conftest.py`.

Before pushing (CI runs the same):

```bash
cd backend && black --check app/ tests/ && isort --check-only app/ tests/ && pytest -q
cd frontend && npm run build
```

## 6. Changing the schema

Edit `backend/app/models/`, then:

```bash
cd backend
alembic revision --autogenerate -m "describe the change"
# Autogenerate misses Postgres enum drops: for every NEW enum, add
#   op.execute("DROP TYPE IF EXISTS <enum_name>")
# at the end of downgrade().
alembic upgrade head && alembic downgrade -1 && alembic upgrade head   # prove the round-trip
```

With Claude Code, `/migrate` does this including the round-trip check.

## Smoke-testing the API by hand

```bash
# Sign up (user_type: founder | engineer | iec_worker | immigrant)
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"founder@test.com","password":"testpass123","user_type":"founder","first_name":"Test"}'

# Log in → access_token + refresh_token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"founder@test.com","password":"testpass123"}'

# Post a job (salary in cents)
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"title":"Backend Engineer","description":"Build stuff","salary_min":9000000,"salary_currency":"CAD","remote_ok":true,"iec_friendly":true}'

# Browse jobs (no auth)
curl "http://localhost:8000/api/jobs?iec_friendly=true"
```

With Claude Code, `/smoke-test` runs a full founder → job → engineer → apply flow including
the 401/403/400 boundaries.

## Docker (optional)

`docker-compose up` starts Postgres, Redis, the backend, and the Vite dev server, then:

```bash
docker-compose exec backend alembic upgrade head
```

Note: `backend/Dockerfile` still uses `python:3.11-slim`, while the project targets 3.13. The
native setup above is the tested path.

## Troubleshooting

- **`psycopg2` fails to install:** install PostgreSQL client headers.
  macOS: `brew install postgresql`. Ubuntu: `sudo apt install libpq-dev`.
- **CORS errors in the browser:** add the frontend origin to `CORS_ORIGINS` in `backend/.env`
  (comma-separated), then restart uvicorn.
- **400 "Invalid host header":** the API hostname isn't in `ALLOWED_HOSTS` (comma-separated,
  wildcards like `*.onrender.com` allowed).
- **Signup shows "Could not reach the server":** `VITE_API_URL` points at the wrong host, or the
  API isn't running. Vite reads `.env` at startup — restart `npm run dev` after changing it.
- **`integer out of range` on money:** your DB predates migration `70317845a84a`; run
  `alembic upgrade head`.
- **`venv/bin/…: bad interpreter` after moving the folder:** venv paths are absolute; delete
  `venv/` and recreate it.
