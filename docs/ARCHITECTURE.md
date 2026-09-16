# Architecture

## Overview

Ascend is a two-sided marketplace connecting hiring companies (starting with
Korean-Canadian founders) with tech talent (starting with engineers in Korea and
IEC working holiday participants in Canada), plus tooling to make cross-border
employment simple: contracts, compliance guides, and payments.

```
┌────────────────────────────┐        ┌────────────────────────────┐
│   Frontend (React + Vite)  │  HTTP  │   Backend (FastAPI)         │
│   - Job board UI            │◄──────►│   - REST API                │
│   - Auth (JWT stored local) │        │   - Auth (JWT)               │
│   - Profile, applications   │        │   - Business logic          │
└────────────────────────────┘        └───────────┬────────────────┘
                                                    │
                          ┌─────────────────────────┼─────────────────────────┐
                          ▼                         ▼                         ▼
                 ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
                 │   PostgreSQL     │      │      Redis       │      │  External APIs   │
                 │  (source of      │      │  (cache, async   │      │  Wise, DocuSign,  │
                 │   truth)         │      │   job queue)     │      │  SendGrid, Google │
                 └─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Guiding principles

1. **Start narrow, design for expansion.** The product starts Korea ⇄ Canada
   specific (visa fields, IEC flag, KRW/CAD), but the schema avoids hardcoding
   country logic where a config value would do — e.g. `location_country` is a
   free ISO code, not an enum of two values.
2. **Boring, proven tech.** FastAPI + PostgreSQL + React is a stack any
   contractor or hire can pick up immediately. No exotic infra.
3. **Compliance content is data, not code.** Contract templates and guide
   content live in the database / CMS-style tables so they can be reviewed by
   a Korean-Canadian accountant/lawyer without a deploy.
4. **Money and legal features ship behind feature flags.** `ENABLE_WISE_PAYMENTS`
   and `ENABLE_DOCUSIGN` in `backend/app/config.py` let us launch the job
   board before payments/contracts are legally reviewed.

## Backend layout

```
backend/app/
├── main.py            # FastAPI app factory, middleware, router registration
├── config.py          # Settings (env vars via pydantic-settings)
├── database.py        # SQLAlchemy engine/session, get_db() dependency
├── dependencies.py     # Shared deps (get_current_user, etc.)
├── models/            # SQLAlchemy ORM models (source of truth for schema)
├── schemas/           # Pydantic request/response models
├── routes/            # FastAPI routers, one per resource
├── services/          # Business logic (auth, and future: contracts, payments)
├── integrations/      # External API clients (Wise, DocuSign, SendGrid) — TODO
└── utils/             # Small shared helpers — TODO
```

Request flow: `routes/*.py` → validates input via `schemas/*.py` → calls
`services/*.py` for logic → reads/writes via SQLAlchemy `models/*.py` →
returns a `schemas/*.py` response model.

## Frontend layout

```
frontend/src/
├── App.tsx            # Route definitions
├── main.tsx           # React root, QueryClientProvider
├── components/        # Reusable UI (Navbar, JobCard, ...)
├── pages/             # Route-level components
├── services/          # Axios API clients (auth.ts, jobs.ts, api.ts)
├── store/             # Zustand stores (authStore)
└── types/             # TypeScript interfaces mirroring backend schemas
```

State strategy: server state (jobs, applications) lives in TanStack Query
caches; only client-only state (the logged-in user object, UI toggles) lives
in Zustand.

## Data model summary

See [DATABASE.md](./DATABASE.md) for full schema. Core entities: `User`,
`Job`, `Application`, `Contract`, `Payment`, `Mentorship`, `Message`.

## Why these entities are separate from "country"

Rather than a `korea_engineer` vs `canada_engineer` split at the User level,
country/visa context lives in fields (`country`, `visa_status`) and in
`Job.location_country` / `iec_friendly` / `visa_sponsorship`. This means
adding a third country (e.g. the Philippines, per the original "expand
globally" goal) requires no schema migration — just new guide content and
contract templates.

## Open architecture decisions (revisit as we build)

- **Messaging:** currently simple polling via `GET /messages`. Will move to
  WebSockets or Server-Sent Events once usage justifies it.
- **Search:** Postgres `ILIKE`/JSON filtering is fine at low job-post volume.
  Revisit with a search index (e.g. Postgres full-text or Meilisearch) if
  job volume grows past a few hundred.
- **Payments:** MVP wraps Wise's API directly from `services/`. If volume or
  compliance needs grow, an `integrations/payments/` abstraction can support
  multiple providers behind one interface.
