# CLAUDE.md — AI-Powered Insurance Simulator

## Project Overview

A simplified fintech platform for an **Introduction to Software Engineering** course. It teaches risk management and micro-insurance through a digital interface. Two audiences use separate frontends backed by a single API + database:

- **End users**: browse, simulate, purchase micro-insurance policies using virtual currency (SimCoin)
- **Insurance company admins**: create products, set risk parameters, monitor APIs, view analytics

The platform demonstrates parametric insurance — automated claims triggered by real-world data (weather, flight status). It is positioned as a third-party software product delivered to an insurance company (the professor's role).

## Architecture

```
frontend-user (Vue 3, port 5173)  ─┐
                                    ├──► backend (FastAPI, port 8000) ──► PostgreSQL 15 (port 5432)
frontend-admin (Vue 3, port 5174) ─┘         │
                                             ├──► Gemini API (AI chatbot)
                                             ├──► OpenWeatherMap (weather triggers)
                                             └──► AviationStack (flight triggers)
```

- **Single backend** serves both frontends via role-based access control (JWT + RBAC)
- **Two separate Vue 3 apps** — no shared runtime state between them
- **Parametric trigger engine** runs as a background task polling external APIs

## Tech Stack

### Backend
- Python 3.10+, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL 15
- Pydantic 2.5+ (validation), PyJWT (auth), bcrypt (passwords)
- httpx (async HTTP), APScheduler (background jobs)
- google-generativeai (Gemini chatbot), numpy (risk calculations)
- pytest (testing)

### Frontend (both apps)
- Vue 3 (Composition API, `<script setup>`), Vite 5, Vue Router 4, Pinia (state)
- TailwindCSS 3.4+ (styling), PrimeVue 4+ (component library)
- Axios (HTTP), ApexCharts via vue3-apexcharts (charts/visualization)

### External APIs
- Google Gemini 2.0 Flash (free: 15 RPM, 1M tokens/day) — AI chatbot
- OpenWeatherMap (free: 60 calls/min) — weather data
- AviationStack (free: 100 requests/month) — flight data

## Project Structure

```
insurance-simulator/              # Root (this repo)
├── backend/                      # FastAPI API server
│   ├── app.py                    # Entry point — FastAPI app + router registration
│   ├── config/                   # Settings (env vars) + DB connection
│   ├── models/                   # SQLAlchemy models (10 tables)
│   ├── schemas/                  # Pydantic request/response schemas
│   ├── routers/                  # API route handlers
│   ├── services/                 # Business logic layer
│   ├── middleware/               # JWT auth middleware
│   ├── utils/                    # Shared helpers
│   ├── alembic/                  # Database migrations
│   ├── seed/                     # Seed data (products, risk data)
│   └── tests/                    # pytest tests
├── frontend-user/                # Vue 3 — End user app
│   └── src/
│       ├── views/                # Page components
│       ├── components/           # Reusable UI (insurance/, simulation/, wallet/, chat/)
│       ├── stores/               # Pinia state (auth, wallet, insurance, notification)
│       ├── services/             # Axios API wrappers
│       └── router/               # Route definitions
├── frontend-admin/               # Vue 3 — Admin dashboard
│   └── src/
│       ├── views/                # Admin pages
│       ├── components/           # Dashboard widgets, tables, charts
│       ├── stores/               # Pinia state
│       ├── services/             # Axios API wrappers
│       └── router/               # Route definitions
├── docker-compose.yml            # Orchestrates all 4 services
├── SPEC.md                       # Full specification (read this first)
├── CLAUDE.md                     # This file
└── README.md                     # Quick start guide
```

## Development Commands

### Backend
```bash
cd backend
python -m venv venv && source venv/Scripts/activate   # Windows
pip install -r requirements.txt
alembic upgrade head                                   # Run migrations
python -m seed.seed_data                               # Seed data
uvicorn app:app --reload --port 8000                   # Run server
pytest                                                 # Run tests
alembic revision --autogenerate -m "description"       # New migration
```

### Frontend (either app)
```bash
cd frontend-user    # or frontend-admin
npm install
npm run dev         # Dev server (user: 5173, admin: 5174)
npm run build       # Production build
npm run lint        # Lint
```

### Docker (all services)
```bash
docker-compose up -d          # Start everything
docker-compose down           # Stop everything
docker-compose logs -f backend
```

## Database Models (10 tables)

| Model | Purpose | Key relationships |
|-------|---------|-------------------|
| User | Auth, profiles, roles (USER/ADMIN) | Has one Wallet, many Policies |
| Wallet | Virtual currency balance | Belongs to User, has many Transactions |
| WalletTransaction | Immutable audit log of all money movements | Belongs to Wallet |
| InsuranceProduct | Product catalog with JSON parameter schemas | Has many Policies, created by Admin |
| Policy | Purchased insurance instance | Belongs to User + Product, has many Claims |
| Claim | Triggered (auto or manual) insurance claim | Belongs to Policy |
| RiskData | Historical event data for probability calculations | Linked by product category |
| Notification | User notifications (claims, payouts, expiry) | Belongs to User |
| ChatSession | AI chatbot conversation history | Belongs to User |
| SimulationSession | Logged simulation interactions | Belongs to User + Product |
| ApiMonitorLog | External API health tracking | Standalone |

See SPEC.md Section 6 for full column definitions, types, constraints, and indexes.

## Key Features

1. **Auth**: Email/password + JWT (access 24h + refresh 7d), RBAC (USER/ADMIN)
2. **Wallet**: Top-up, premium deduction, claim payout, refund. Balance never negative.
3. **Insurance Catalog**: 5 product types, JSON-schema-driven forms, dynamic premium calculation
4. **Policy Purchase**: Calculate premium → validate wallet → deduct → create ACTIVE policy
5. **Automated Claims**: Background job checks external APIs against active policy triggers
6. **AI Chatbot**: Gemini-powered advisor on Insurance Detail page, context-aware
7. **Risk Engine**: Historical probability calculations, risk scores (1-10 for users, detailed for admins)
8. **Simulation**: Interactive trigger explorer (sliders + threshold visualization + "Activated!" popup) on Detail page
9. **Notifications**: Claim triggered, payout received, policy expiring/expired, system announcements
10. **Admin Dashboard**: Metrics, product CRUD, claims management, risk analytics, API monitoring

## Insurance Products (5 types)

| Product | Trigger | API Source |
|---------|---------|------------|
| Flight Delay Protection | Delay >= threshold or cancelled | AviationStack |
| Crop Weather Insurance | Weather metric exceeds threshold | OpenWeatherMap |
| Gadget Repair Coverage | Manual claim with evidence (non-parametric) | None |
| Typhoon Insurance | Severe weather alert >= threshold | OpenWeatherMap |
| Rainfall Event Insurance | Rainfall on event date > threshold | OpenWeatherMap |

Products are defined by JSON schemas (`parameters_schema` + `trigger_conditions`). Admins add new products by providing these JSON configs — no code changes needed.

## API Design

Base URL: `http://localhost:8000/api/v1`

Key endpoint groups: `/auth`, `/wallet`, `/insurance/products`, `/policies`, `/claims`, `/simulation`, `/chat`, `/notifications`, `/admin`

See SPEC.md Section 7 for full endpoint table.

## Coding Conventions

### Python
- Black formatter (line 88), Ruff linter
- snake_case functions/vars, PascalCase classes, UPPER_SNAKE_CASE constants
- Type hints on all function signatures
- async def for all route handlers and I/O service methods
- Layered: Router → Service → Model (routers never touch DB directly)

### JavaScript/Vue
- Prettier + ESLint with eslint-plugin-vue
- Composition API with `<script setup>` only (no Options API)
- PascalCase components, camelCase functions, kebab-case CSS
- API calls only in services/ files, never in components
- Pinia for state management

### Git
- Conventional Commits: feat:, fix:, refactor:, docs:, test:
- Branch naming: feature/, fix/, db/

## Development Phases

1. **Phase 1 — Foundation**: DB models, auth, wallet, catalog, purchase, basic claims, basic UI
2. **Phase 2 — Intelligence**: AI chatbot, risk engine, simulation mode, charts, admin analytics
3. **Phase 3 — Real-World Integration**: External API connections, trigger monitor, API health dashboard
4. **Phase 4 — Polish**: UI/UX, error handling, performance, security, Docker deployment

## Team

- 5 members total
- Database branch (2 members): All database-related work — models, schemas, DB connection, migrations, seed data
- Other members handle frontend, business logic, AI integration

## Boundaries

### Always
- Validate inputs server-side, use parameterized queries
- Hash passwords with bcrypt, use DB transactions for multi-step ops
- Log all wallet transactions immutably
- Keep two frontends independent

### Never
- Store plaintext passwords
- Allow wallet balance to go negative
- Delete wallet transactions (append-only)
- Let chatbot execute actions (advisory only)
- Skip database migrations
- Store real financial data

### Ask First
- Before adding new insurance product categories
- Before changing premium calculation formula
- Before adding new external API dependencies
- Before modifying DB schema after Phase 1 delivery
