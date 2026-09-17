# Ascend 🚀

**Connecting Korean-Canadian tech professionals with global talent. Professional growth across borders.**

## Mission

Ascend is a platform that connects:
- **Korean-Canadian founders & CTOs** hiring engineers globally (starting with Korea)
- **IEC working holiday participants** and international tech talent seeking careers in Canada
- **Remote professionals** across countries with seamless payments and compliance support

We bridge the gap between opportunity and talent, making cross-border hiring simple, trustworthy, and affordable.

## Why Ascend?

### For Founders/Hiring Managers
- Pre-vetted talent pool from Korea and beyond
- 1-click employment contracts and compliance checklists
- No EOR middleman markup (we integrate Wise for payments)
- Grow your global team affordably

### For Tech Talent
- Jobs curated for your visa status (IEC, permanent residency, remote)
- Mentorship from established Korean-Canadian professionals
- Simplified cross-border payments and tax guidance
- A community that understands your journey

### For the Ecosystem
- Reduce brain drain: keep Korean-Canadian talent engaged
- Unlock global engineering talent for Canadian startups
- Support immigrant professionals with contextual guidance
- Building trust through transparency and community

## Project Status

🔨 **MVP Development (Phase 1-2)**
- Weeks 1-6: Core marketplace (job board, profiles, messaging, knowledge base)
- Weeks 7-12: Employment tooling (contracts, compliance, tax guides)
- Weeks 13-18: Payments & community (Wise integration, mentorship)

**Current milestone:** Project setup and initial architecture

## Tech Stack

### Backend
- **Runtime:** Python 3.11+
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Cache:** Redis
- **Task Queue:** Celery (async jobs)
- **ORM:** SQLAlchemy

### Frontend
- **Framework:** React 18 + TypeScript
- **Styling:** Tailwind CSS
- **State:** Zustand
- **HTTP Client:** TanStack Query
- **Mobile:** Responsive design (mobile-first)

### Infrastructure
- **Hosting:** Render.com or AWS
- **CI/CD:** GitHub Actions
- **Container:** Docker
- **Error Tracking:** Sentry

### Integrations
- **Auth:** Google OAuth 2.0
- **Payments:** Wise API
- **Email:** SendGrid / Resend
- **E-Signatures:** DocuSign

## Project Structure

```
Ascend/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py      # FastAPI app entry
│   │   ├── config.py    # Environment config
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas (validation)
│   │   ├── routes/      # API endpoints
│   │   ├── services/    # Business logic
│   │   ├── utils/       # Helper functions
│   │   └── integrations/# External API clients
│   ├── migrations/       # Alembic database migrations
│   ├── tests/            # Unit & integration tests
│   ├── requirements.txt  # Python dependencies
│   ├── Dockerfile        # Container config
│   └── .env.example      # Environment template
├── frontend/             # React application
│   ├── public/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # API client, utilities
│   │   ├── store/        # Zustand state management
│   │   ├── types/        # TypeScript interfaces
│   │   ├── styles/       # Global styles
│   │   └── App.tsx
│   ├── package.json
│   └── .env.example
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md   # System design
│   ├── API.md            # API documentation
│   ├── DATABASE.md       # Database schema
│   ├── SETUP.md          # Dev environment setup
│   ├── PRODUCT.html      # Product roadmap (plan artifact)
│   └── GUIDES/           # Knowledge base content
│       ├── korea-employment/
│       ├── canadian-taxes/
│       ├── visa-immigration/
│       └── cross-border-payments/
├── public/               # Static assets
│   └── images/
├── .gitignore
├── docker-compose.yml    # Local dev containers
├── README.md             # This file
└── CONTRIBUTING.md       # Contribution guidelines

```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your config

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- API Docs (Swagger): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Docker (All-in-One)

```bash
docker-compose up
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379
- Backend API on port 8000
- Frontend dev server on port 5173

## API Overview

**Base URL:** `http://localhost:8000/api`

### Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/auth/signup` | Register user |
| `POST` | `/auth/login` | Login user |
| `GET` | `/jobs` | Browse jobs (with filters) |
| `POST` | `/jobs` | Create job (founders) |
| `POST` | `/applications` | Apply to job |
| `GET` | `/profile/me` | Get current user profile |
| `POST` | `/contracts` | Generate employment contract |
| `POST` | `/payments` | Initiate Wise payment |
| `GET` | `/knowledge/guides` | Browse knowledge base |

Full API documentation: See `docs/API.md` and `http://localhost:8000/docs`

## Database Schema

Core entities:
- **Users** - Profiles, authentication, user metadata
- **Jobs** - Job postings from founders
- **Applications** - User applications to jobs
- **Contracts** - Employment agreements
- **Payments** - Cross-border transactions
- **Mentorships** - Mentor-mentee relationships
- **Messages** - In-app messaging

Full schema: See `docs/DATABASE.md`

## Product Roadmap

### Phase 1: Core Marketplace (Weeks 1-6)
- ✅ User authentication & profiles
- ✅ Job board with filters
- ✅ Apply to jobs
- ✅ In-app messaging
- ✅ Basic knowledge base

### Phase 2: Employment Tooling
- [x] Contract template generation (draft → send → sign/cancel, typed term validation)
- [ ] E-signature integration — wired behind `ENABLE_DOCUSIGN`, needs credentials
- [ ] Tax/visa compliance checklists — needs professional review
- [ ] Employment guides (Korea, Canada) — placeholder page, needs professional review

### Phase 3: Payments & Community
- [x] Payment records (ledger) — real transfers behind `ENABLE_WISE_PAYMENTS`, needs credentials
- [x] Mentorship requests (request → accept/decline → complete)
- [x] In-app messaging (threads, polling)
- [ ] Mentor directory — needs a `User` flag + migration
- [ ] Community Slack/Discord

### Launch readiness (no external input needed)
- [x] Token refresh + session restore on reload
- [x] Production config guards (`SECRET_KEY`, env-driven CORS/hosts)
- [x] Render blueprint, CI, deploy guide — see `docs/DEPLOY.md`
- [x] Draft Terms / Privacy pages (marked as unreviewed)
- [ ] Password reset / email verification — needs an email provider

### Phase 4: Launch & Scale (Weeks 19-20+)
- [ ] Analytics & monitoring
- [ ] Public launch
- [ ] Marketing campaigns
- [ ] Global expansion prep

Full roadmap: See `docs/PRODUCT.html`

## Deploy

One-click Render blueprint (`render.yaml`) with managed Postgres; CI runs the test
suite and frontend build on every push. Step-by-step: `docs/DEPLOY.md`.

## Contributing

We're building this in public and welcome feedback, suggestions, and contributions.

- **Found a bug?** Open an issue
- **Have an idea?** Start a discussion
- **Want to contribute?** See `CONTRIBUTING.md`

## Development Guidelines

### Code Style
- **Python:** Black formatter, isort imports, type hints
- **TypeScript/React:** ESLint, Prettier

### Testing
- **Backend:** pytest with coverage
- **Frontend:** Vitest, React Testing Library

### Git Workflow
1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit with clear messages
3. Push and create a pull request
4. CI/CD runs tests; get reviewed; merge

### Commits
```
Format: <type>: <description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Code style (no logic change)
- refactor: Refactoring
- test: Adding/updating tests
- chore: Dependencies, config
```

## License

MIT License - See LICENSE file

## Support & Community

- **Discord:** [Coming soon]
- **Email:** hello@ascendtalent.com
- **Twitter:** [@ascendtalent](https://twitter.com)
- **Issues:** GitHub Issues

## Acknowledgments

Built for Korean-Canadians, immigrants, and global tech talent seeking opportunity and growth.

---

**Status:** MVP in development  
**Last updated:** September 2026  
**Maintainer:** [Your name]
