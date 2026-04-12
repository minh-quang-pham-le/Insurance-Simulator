# AI-Powered Insurance Simulator

## The Topic
The system features a simplified fintech platform designed to introduce users to the concepts of risk management and micro-insurance through a digital interface. Users can browse and "purchase" small-scale, short-term insurance policies—such as flight delay protection, crop weather insurance, or gadget repair coverage—using virtual currency. This core functionality aims to demonstrate how insurance premiums are calculated and how risk pooling works in a modern, accessible financial environment.

Furthermore, the application must incorporate an "Automated Claims Processing" engine that uses real-world data triggers (such as weather reports or flight status APIs) to automatically settle claims. When a predefined "event" occurs, the system will instantly credit the user's virtual wallet, illustrating the efficiency of parametric insurance models. There will also be a "simulation" mode, allowing users to quickly see if an insurance plan is suitable for them or not.

## The Project
A simplified fintech platform that introduces users to risk management and micro-insurance through a digital interface. Built for the **Introduction to Software Engineering** course.

## What It Does

- **Users** browse and purchase small-scale, short-term insurance policies (flight delay, crop weather, gadget, typhoon, rainfall) using virtual currency (SimCoin)
- **Automated Claims** — parametric insurance triggers auto-settle claims using real-world data (weather APIs, flight status)
- **AI Chatbot** — LLM-powered advisor helps users make informed purchase decisions
- **Risk Engine** — statistical probability calculations from historical data
- **Simulation Mode** — interactive trigger explorer showing exactly when insurance activates
- **Admin Dashboard** — insurance company manages products, monitors claims, views analytics

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy 2.0, PostgreSQL 15 |
| Frontend | Vue 3, Vite, TailwindCSS, PrimeVue, ApexCharts |
| AI | Google Gemini 2.0 Flash |
| External APIs | OpenWeatherMap, AviationStack |
| Infrastructure | Docker, Docker Compose |

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15 (or Docker)

### Option 1: Docker (recommended)
```bash
git clone <repo-url>
cd insurance-simulator
docker-compose up -d
```
- User App: http://localhost:5173
- Admin Dashboard: http://localhost:5174
- API Docs: http://localhost:8000/docs
- Database: localhost:5432

### Option 2: Manual
```bash
# Backend
cd backend
python -m venv venv
source venv/Scripts/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Edit with your DB credentials
alembic upgrade head
python -m seed.seed_data
uvicorn app:app --reload --port 8000

# Frontend (in separate terminals)
cd frontend-user && npm install && npm run dev
cd frontend-admin && npm install && npm run dev
```

## Project Structure

```
├── backend/              # FastAPI API server
├── frontend-user/        # Vue 3 — End user app (port 5173)
├── frontend-admin/       # Vue 3 — Admin dashboard (port 5174)
├── docker-compose.yml    # All services orchestration
├── SPEC.md               # Full specification
└── CLAUDE.md             # AI assistant context
```

## Documentation

- **[SPEC.md](SPEC.md)** — Full specification: features, data models, API design, architecture
- **[CLAUDE.md](CLAUDE.md)** — AI development context

## Team

5 members — Introduction to Software Engineering course project.
