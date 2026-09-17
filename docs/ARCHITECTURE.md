# Architecture

## Overview

Ascend is a two-sided marketplace connecting hiring companies (starting with Korean-Canadian
founders) with tech talent (engineers in Korea and Canada, IEC working-holiday participants,
newcomers), plus tooling for cross-border employment: contracts, mentorship, messaging, and
payment records.

```
            Browser
               │
               ▼
┌──────────────────────────────┐   HTTPS + JSON   ┌──────────────────────────────┐
│ ascend-web (Render static)   │ ───────────────► │ ascend-api (Render web)      │
│ React + Vite SPA             │   Bearer JWT     │ FastAPI + uvicorn            │
│ - TanStack Query cache       │ ◄─────────────── │ - TrustedHost → CORS → routes│
│ - Zustand auth store         │                  │ - slowapi limits on /auth/*  │
│ - axios refresh-on-401       │                  │ - alembic upgrade on start   │
└──────────────────────────────┘                  └───────┬──────────────┬───────┘
                                                          │              │
                                                          ▼              ▼
                                               ┌────────────────┐  ┌────────────────────┐
                                               │ ascend-db      │  │ External (optional)│
                                               │ PostgreSQL 16  │  │ SendGrid — live    │
                                               │ source of truth│  │   when key is set  │
                                               └────────────────┘  │ Wise, DocuSign —   │
                                                                   │   flagged off      │
                                                                   └────────────────────┘
```

No Redis, queue, or worker processes run today. Everything is synchronous request/response
on a single API instance.

## Guiding principles

1. **Start narrow, design for expansion.** Korea ⇄ Canada specifics (IEC flag, visa fields,
   KRW/CAD) live in data fields, not in user types or country enums — `location_country` is a
   free ISO code, so adding a third country needs no migration.
2. **Boring, proven tech.** FastAPI + PostgreSQL + React; no exotic infrastructure.
3. **Money and legal features ship behind flags and honest copy.** `ENABLE_WISE_PAYMENTS` and
   `ENABLE_DOCUSIGN` stay off until reviewed; the UI says payments are records, signing is an
   acknowledgment, and templates are not legal advice.
4. **Never lose a counterparty's records.** Users are anonymized, not deleted.
5. **Privacy by default.** Other users never see an email or phone number; names fall back to
   "User #id", never to an email local-part.

## Backend

```
backend/app/
├── main.py          # create_app(): TrustedHostMiddleware, CORS, slowapi, routers, /health
├── config.py        # pydantic-settings; cors_origins_list / allowed_hosts_list; SECRET_KEY guard
├── database.py      # engine, SessionLocal, get_db()
├── dependencies.py  # get_current_user — decodes access JWT, requires status == active
├── models/          # ORM (source of truth); BaseModel adds id + tz-aware timestamps
├── schemas/         # Pydantic in/out; UserResponse (self) vs PublicUserResponse (others)
├── routes/          # auth, profile, jobs, applications, contracts, payments, mentorships, messages
├── services/
│   ├── auth.py      # bcrypt, JWT access/refresh, reset + verify tokens
│   ├── contracts.py # template registry + typed required-term validation
│   ├── email.py     # EmailSender: Console (default) | SendGrid | Recording (tests)
│   └── ratelimit.py # slowapi Limiter keyed on first X-Forwarded-For
├── utils/names.py   # display_name()
└── integrations/    # empty — Wise / DocuSign clients will live here
```

Request flow: `routes/*` validate with `schemas/*` → authorize (creator / party checks inline)
→ optional `services/*` logic → SQLAlchemy `models/*` → response schema.

Authorization is per-resource and explicit in each route (e.g. only the job creator lists
applications; only the applicant signs; only the sender cancels a payment). There is no
role-based middleware; `user_type` shapes the UI, not API permissions — any active user may
post a job.

### Auth

- **Access token:** JWT, 30 min, `type=access`. **Refresh token:** JWT, 7 days, `type=refresh`,
  stateless (no revocation list yet).
- **Password reset token:** signed JWT carrying a fingerprint of the current password hash, so
  it dies as soon as the password changes (single use).
- **Email verification token:** signed JWT, 24 h. Verify/refresh/reset all re-check that the
  account is still active.
- Frontend stores tokens in `localStorage`; `services/api.ts` retries a 401 once after refresh,
  and `AuthBootstrap` restores the user on page load.

### Email

`get_email_sender()` returns the SendGrid sender when `SENDGRID_API_KEY` is set, otherwise the
console sender, which logs the full message (links included) to stdout — that's how reset links
reach testers on Render today.

### Rate limiting

slowapi, in-memory, on every `/auth/*` route except `GET /auth/me`. Limits are per client IP
(first `X-Forwarded-For` hop, since Render sits behind a proxy). In-memory storage only works
on one instance; move to Redis before scaling out.

## Frontend

```
frontend/src/
├── App.tsx          # 25 routes, AuthBootstrap, Navbar, VerifyEmailBanner, Footer
├── main.tsx         # React root, QueryClientProvider
├── pages/           # one component per route
├── components/      # Navbar (mobile menu), Footer, VerifyEmailBanner, MessageButton, ...
├── content/         # landing.ts — all KO/EN landing copy
├── hooks/           # useReveal (scroll-triggered animation)
├── services/        # axios clients per resource; api.ts (base URL normalize + refresh)
├── store/           # authStore (Zustand)
├── types/           # mirrors backend schemas; PublicUser = User minus email
├── utils/           # formatCents, formatDateOnly
└── styles/          # Tailwind entry, keyframes, reduced-motion handling
```

- **Server state** (jobs, contracts, threads, …) lives in TanStack Query caches; mutations
  invalidate the relevant keys. **Client state** (current user) lives in Zustand.
- **Messaging** polls: `GET /messages/threads` every 15 s, an open thread every 5 s.
- **Landing page** is the only page that fetches without auth on load (`GET /jobs` for the
  live roles strip). Its animations are CSS keyframes plus an IntersectionObserver hook, with
  `prefers-reduced-motion` respected — no animation library.
- **Dates:** date-only strings go through `formatDateOnly` (parsing them with `new Date()`
  shifts them a day west of UTC).

## Deployment

Render blueprint (`render.yaml`): `ascend-db` (Postgres), `ascend-api` (runs
`alembic upgrade head && uvicorn …`, health check `/health`), `ascend-web` (static build with an
SPA rewrite to `index.html`). `VITE_API_URL` is baked in at build time. CI (GitHub Actions)
runs black/isort + pytest against a Postgres service, and the frontend type-check + build.
Details: [DEPLOY.md](./DEPLOY.md).

## Open decisions

- **Messaging transport:** polling is fine at current volume; move to SSE or WebSockets when
  thread counts grow.
- **Search:** Postgres filters are fine for hundreds of jobs; revisit full-text or Meilisearch later.
- **Payments:** wrap Wise in `integrations/` behind an interface so a second provider fits.
- **Guides / templates as data:** templates are code today (`services/contracts.py`) so they're
  validated and versioned; move reviewable copy to the DB once a professional reviewer is involved.
- **Framework:** staying on Vite SPA; if SEO or SSR becomes important, React Router v7
  framework mode is the lower-cost path than a Next.js rewrite.
