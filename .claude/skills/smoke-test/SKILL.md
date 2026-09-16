---
name: smoke-test
description: Run the end-to-end API smoke test — migrations, then a real founder→job→engineer→apply flow over HTTP that checks happy paths and every 401/403/400 boundary. Use after any change to backend routes, models, or auth, and before declaring backend work done.
user-invocable: true
allowed-tools:
  - Bash
  - Read
---

# /smoke-test

Runs the API against a real Postgres and asserts exact HTTP codes. Do not "simulate" this;
if the DB is unreachable, stop and say so.

## 1. Preconditions
```bash
cd backend && source venv/bin/activate
grep ^DATABASE_URL .env            # must exist (copy .env.example if not)
pg_isready -h localhost -p <port from URL>
```
If Postgres is not reachable, stop and point the user to `docs/SETUP.md`.
Never start a system service (`brew services`) yourself.

## 2. Migrate to head, then prove the round-trip
```bash
alembic upgrade head && alembic downgrade base && alembic upgrade head
psql "<DATABASE_URL>" -tAc "SELECT count(*) FROM pg_type WHERE typtype='e'"   # after downgrade must be 0
```

## 3. Run the flow
Start `uvicorn app.main:app --port 8000` in the background (trap + kill it at the end),
wait for `/health`, then walk these with `curl` and assert the code in parentheses:

| # | Step | Expect |
|---|------|--------|
| 1 | signup founder | 201 |
| 2 | duplicate signup | 400 |
| 3 | login founder → save token | 200 |
| 4 | login wrong password | 401 |
| 5 | POST /jobs with token | 201 → save job id |
| 6 | POST /jobs without token | 401 |
| 7 | GET /jobs?iec_friendly=true (public) | 200, contains the job |
| 8 | signup + login engineer → save token | 201 / 200 |
| 9 | POST /applications as engineer | 201 |
| 10 | apply again | 400 |
| 11 | GET /applications/me as engineer | 200, 1 item |
| 12 | GET /applications/job/{id} as founder | 200, 1 item |
| 13 | GET /applications/job/{id} as engineer | 403 |
| 14 | PUT /applications/{id} status=interviewing as founder | 200 |
| 15 | PUT /jobs/{id} as engineer | 403 |
| 16 | GET /auth/me with garbage token | 401 |
| 17 | GET /profile/{engineer id} (public) | 200, no `password_hash` key |

Use fresh emails each run (suffix a timestamp) so re-runs do not collide on step 2.
Add a row for any endpoint you just built — this table is the regression suite until pytest exists.

## 4. Log check
`grep -cE "WARNING|ERROR|Traceback" <uvicorn log>` must print `0`. Anything else is a finding.

## 5. Report
One line per step with actual vs expected; then PASS / FAIL with the failing steps listed.
Do not summarise a failure as "mostly works".
