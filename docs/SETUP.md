# Local Development Setup

## Option A: Docker (recommended, fewest moving parts)

```bash
docker-compose up
```

This starts Postgres, Redis, the backend (with hot reload), and the frontend
dev server together. First run will build images, which takes a few minutes.

Then, in a second terminal, run migrations inside the backend container:
```bash
docker-compose exec backend alembic upgrade head
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Option B: Running natively

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ running locally
- Redis 7+ running locally (only needed once async jobs/payments land)

### 1. Database

Create the dev database:
```bash
createdb ascend_dev
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: at minimum set DATABASE_URL to match your local Postgres

alembic upgrade head
uvicorn app.main:app --reload
```

API is now live at http://localhost:8000 (docs at `/docs`).

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App is now live at http://localhost:5173.

## Creating your first migration

Models already exist in `backend/app/models/`, but no migration has been
generated yet. After setting up the database connection:

```bash
cd backend
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

Review the generated file in `migrations/versions/` before running it against
anything but a throwaway local database.

## Smoke-testing the API

```bash
# Sign up
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"founder@test.com","password":"testpass123","user_type":"founder","first_name":"Test"}'

# Log in
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"founder@test.com","password":"testpass123"}'

# Use the returned access_token to post a job
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"title":"Backend Engineer","description":"Build stuff","remote_ok":true,"iec_friendly":true}'

# Browse jobs (no auth needed)
curl http://localhost:8000/api/jobs
```

## Troubleshooting

- **`psycopg2` fails to install:** you need PostgreSQL client headers.
  macOS: `brew install postgresql`. Ubuntu: `sudo apt install libpq-dev`.
- **CORS errors in the browser:** confirm the frontend origin is listed in
  `CORS_ORIGINS` in `backend/app/config.py`.
- **401 on every request after login:** check that `VITE_API_URL` in the
  frontend `.env` matches where the backend is actually running.
