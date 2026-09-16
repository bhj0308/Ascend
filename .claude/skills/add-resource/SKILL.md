---
name: add-resource
description: Add a new backend API resource (routes + schemas, using an existing or new SQLAlchemy model) following this repo's exact pattern, then register, verify, and document it. Use when asked to expose Contract, Payment, Mentorship, Message, or any new entity over the API.
user-invocable: true
---

# /add-resource <name>

The Contract, Payment, Mentorship and Message models **already exist** in `backend/app/models/`
with matching schemas in `backend/app/schemas/` (except message/mentorship — check first).
Most of this skill is writing one `routes/<name>.py` file. Do not redesign the model unless asked.

## Steps
1. **Read the references first** — `routes/jobs.py`, `routes/applications.py`,
   `schemas/job.py`. Match their shape exactly: `router = APIRouter()`, `Depends(get_db)`,
   `Depends(get_current_user)`, `response_model=`, explicit status codes.
2. **Schema** — if `schemas/<name>.py` is missing, create `Create`, `Update`, `Response`
   classes. `Response` uses `model_config = ConfigDict(from_attributes=True)`.
   Never put `password_hash` or hiring-side `notes` in a public response.
3. **Routes** — `routes/<name>.py`. Decide and *write down in a docstring* who may do what:
   - who can create (any authed user? founder only?)
   - who can read (owner? both parties? public?)
   - who can update/delete (owner only → 403 otherwise)
   - what is a conflict (400) vs missing (404)
4. **Register** — in `app/main.py`:
   `app.include_router(<name>.router, prefix="/api/<name>s", tags=["<Name>s"])`
   and add it to the `from app.routes import ...` line.
5. **Format + import check**
   ```bash
   black app/ && isort app/
   python -c "from app.main import app; print(sorted(p for p in app.openapi()['paths'] if '<name>' in p))"
   ```
6. **Verify over HTTP** — run `/smoke-test` and add rows for the new endpoints, including
   at least one 403 (wrong user) and one 401 (no token).
7. **Document** — add the endpoints to `docs/API.md` and remove them from its
   "Not yet implemented" list. Add a `frontend/src/types/index.ts` interface if the
   frontend will consume it.

## Gotchas specific to the pending resources
- **Payment**: never move real money here yet — `ENABLE_WISE_PAYMENTS` is a feature flag in
  `config.py`; routes should create `PENDING` rows and return 501/`{"detail": "payments disabled"}`
  when the flag is off. Amounts are integer cents.
- **Contract**: the `terms` JSON is free-form per template; validate at least `salary`,
  `currency`, `start_date`. Legal-adjacent — add the "not legal advice" note to the docstring.
- **Mentorship**: both mentor and mentee may read; only the *mentor* accepts/declines
  (`REQUESTED → ACTIVE|DECLINED`); either may mark `COMPLETED`.
- **Message**: recipient must be a real user (404 otherwise); only sender or recipient may read a thread.
