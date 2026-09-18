# Ascend 🚀

**A tech-talent marketplace for Korean-Canadian founders, engineers in Korea and Canada, and
IEC working-holiday / newcomer talent breaking into Canadian tech.**

- Live app: https://ascend-web-irk7.onrender.com
- Live API: https://ascend-api-onu3.onrender.com/health

## Mission

Ascend connects:
- **Korean-Canadian founders & CTOs** hiring engineers across Korea and Canada
- **IEC working-holiday participants and immigrants** looking for tech work in Canada
- **Remote professionals** who need contracts, mentorship, and payment records in one place

### For founders / hiring managers
- Post jobs and flag them as IEC-friendly, visa-sponsoring, or remote-OK
- Generate cross-border contract drafts from templates (Korea ⇄ Canada, contractor, full/part-time)
- Keep a payment record per contract for documentation

### For tech talent
- Filter jobs by visa situation (IEC-friendly, sponsorship, remote)
- Find a mentor who has already made the move, and request mentorship from their profile
- Message founders directly — no recruiter in the middle

## Project status (September 2026)

**MVP is live on Render (free tier, early access).** Everything below is built, tested, and deployed.

| Area | What works | What's still a placeholder |
|---|---|---|
| Auth | Signup/login, JWT access + refresh, session restore, password reset, email verification, rate limiting on `/auth/*` | Emails print to the API log until `SENDGRID_API_KEY` is set; Google OAuth not wired |
| Profiles | Editor, public profiles (no email exposed), mentor opt-in, anonymizing account deletion | Avatars |
| Jobs | CRUD, visa/IEC/remote filters, applications pipeline (applied → hired) | Search beyond filters |
| Contracts | 5 templates with validated terms, draft → send → sign / cancel | DocuSign (`ENABLE_DOCUSIGN`); in-app signing is an acknowledgment, not a legal e-signature |
| Payments | Ledger records (pending / cancelled), per-counterparty history | Real transfers via Wise (`ENABLE_WISE_PAYMENTS`); `execute` returns 501 |
| Mentorship | Directory, request → accept/decline → complete | — |
| Messaging | Threads, unread counts, polling (15s list / 5s thread) | WebSockets |
| Guides | Page with topic outlines | Real content (needs professional review) |
| Landing | Animated KO/EN landing page with live open-roles feed | — |

Numbers: 40 API paths (46 operations), 25 frontend routes, 91 backend tests.

## Tech stack (what's actually in use)

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16, PyJWT, bcrypt,
  slowapi (rate limiting), pydantic-settings, SendGrid (optional)
- **Frontend:** React 18, TypeScript, Vite 6, Tailwind CSS 3, React Router 6, TanStack Query 5
  (server state), Zustand (auth state), axios
- **Infra:** Render blueprint (`render.yaml`: managed Postgres + API web service + static site),
  GitHub Actions CI (black/isort + pytest against Postgres; frontend `tsc` + build)
- **Wired but inactive:** Wise, DocuSign, Sentry, Google OAuth settings exist in config behind
  flags or blank keys. Redis/Celery are in `requirements.txt` and `docker-compose.yml` but no
  code uses them yet.

## Project structure

```
Ascend/
├── backend/
│   ├── app/
│   │   ├── main.py          # App factory, middleware (CORS, trusted hosts, rate limit), routers
│   │   ├── config.py        # Settings from env; production SECRET_KEY guard
│   │   ├── dependencies.py  # get_current_user (rejects inactive accounts)
│   │   ├── models/          # SQLAlchemy ORM — source of truth for the schema
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── routes/          # One router per resource (auth, profile, jobs, applications,
│   │   │                    #   contracts, payments, mentorships, messages)
│   │   ├── services/        # auth (JWT/bcrypt), contracts (templates), email, ratelimit
│   │   ├── utils/           # names.py (display_name)
│   │   └── integrations/    # empty — Wise/DocuSign clients go here
│   ├── migrations/          # Alembic (4 revisions)
│   ├── scripts/seed.py      # Demo dataset through the real API
│   └── tests/routes/        # pytest against real Postgres
├── frontend/
│   └── src/
│       ├── pages/           # One component per route
│       ├── components/      # Navbar, Footer, VerifyEmailBanner, MessageButton, ...
│       ├── content/         # landing.ts — KO/EN landing copy
│       ├── services/        # axios clients per resource (api.ts handles token refresh)
│       ├── store/           # authStore (Zustand)
│       ├── types/           # Mirrors backend schemas
│       ├── utils/           # money + date formatting
│       └── styles/          # Tailwind entry + animation utilities
├── docs/                    # ARCHITECTURE, API, DATABASE, SETUP, DEPLOY, DEMO_ACCOUNTS, PRODUCT.html
├── .claude/                 # Claude Code agents + skills (/feature, /add-resource, /migrate, /smoke-test)
├── render.yaml              # Render blueprint
└── docker-compose.yml       # Optional local containers
```

## Getting started

Full walkthrough, including the test database: [docs/SETUP.md](docs/SETUP.md).

```bash
# Backend (needs a local Postgres)
cd backend
python3.13 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # set DATABASE_URL
alembic upgrade head
uvicorn app.main:app --reload   # http://localhost:8000  (Swagger at /docs)

# Frontend
cd frontend
npm install
cp .env.example .env
npm run dev                     # http://localhost:5173
```

### Demo data

Seed a realistic dataset (10 accounts, 7 jobs, applications, contracts, mentorships,
messages, payment records) so every page has something to click:

```bash
cd backend
python scripts/seed.py            # prints the accounts; all use password demo-pass-2026
python scripts/seed.py --reset    # remove and recreate the demo rows
```

Try `jihoon@example.com` (founder with applicants and contracts) or `yuna@example.com`
(IEC engineer with a contract to sign). What every account shows: [docs/DEMO_ACCOUNTS.md](docs/DEMO_ACCOUNTS.md).
To seed the live site from your laptop: [docs/DEPLOY.md §2b](docs/DEPLOY.md).

## API overview

**Base URL:** `http://localhost:8000/api` locally, `https://ascend-api-onu3.onrender.com/api` live.

| Resource | Highlights |
|---|---|
| `/auth` | signup, login, refresh, me, forgot/reset password, send/verify email |
| `/profile` | `me` (GET/PUT/DELETE), public `/{id}` |
| `/jobs` | browse with filters, CRUD (creator only) |
| `/applications` | apply, mine, per-job list and status updates (job creator) |
| `/contracts` | templates, generate, update draft, send, sign, cancel |
| `/payments` | record, list, cancel; `execute` is 501 until Wise |
| `/mentorships` | mentor directory, request, accept/decline/complete |
| `/messages` | threads, history with a user (marks read), send |

Every endpoint with its error cases: [docs/API.md](docs/API.md). Swagger UI at `/docs` (disabled in production).

## Development

```bash
cd backend && black app/ tests/ scripts/ && isort app/ tests/ scripts/   # CI enforces app/ and tests/
cd backend && pytest -q                                                  # 91 tests, needs ascend_test DB
cd frontend && npm run build                                             # tsc + vite, must pass
```

- **Frontend tests / lint:** `vitest` and `eslint` are installed but not set up yet — there are
  no test files and no ESLint config, so `npm test` and `npm run lint` don't do anything useful.
  `npm run build` (type-check) is the current gate.
- Contribution workflow and commit format: [CONTRIBUTING.md](CONTRIBUTING.md).
- Deploying: [docs/DEPLOY.md](docs/DEPLOY.md).

## Roadmap

### Done
- [x] Auth, profiles, job board with visa filters, applications pipeline
- [x] Contract templates (draft → send → sign/cancel, typed term validation)
- [x] Payment ledger, mentorship, mentor directory, messaging
- [x] Password reset, email verification, rate limiting, anonymizing account deletion
- [x] Render deploy, CI, draft Terms/Privacy, KO/EN landing page, demo seed script

### Needs external input
- [ ] SendGrid key so emails are actually sent
- [ ] Wise and DocuSign credentials (integrations are flagged off)
- [ ] Professional review of contract templates, guides, Terms and Privacy
- [ ] Guide content (Korea employment, Canadian tax, visas, cross-border payments)

### Next engineering work
- [ ] Refresh-token revocation, Redis-backed rate limiting before scaling past one instance
- [ ] Frontend test + lint setup
- [ ] Analytics and monitoring (Sentry DSN)
- [ ] Community (Slack/Discord), public launch

Original plan and phases: [docs/PRODUCT.html](docs/PRODUCT.html).

## License

No license has been chosen yet — there is no `LICENSE` file, so all rights are reserved by default.

---

**Status:** MVP live, early access · **Last updated:** September 2026 · **Maintainer:** Jay Park
