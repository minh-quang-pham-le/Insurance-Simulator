import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from services.trigger_monitor import run_trigger_check

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_trigger_check,
        "interval",
        minutes=settings.TRIGGER_CHECK_INTERVAL_MINUTES,
        id="trigger_check",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"Trigger monitor started — interval: {settings.TRIGGER_CHECK_INTERVAL_MINUTES}m"
    )

    yield

    scheduler.shutdown(wait=False)
    logger.info("Trigger monitor stopped")


app = FastAPI(
    title=settings.APP_TITLE,
    description="AI-Powered Insurance Simulator API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — allow both frontend apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# --- Register routers ---
from routers import auth, wallet, insurance, policies, claims, notifications, admin

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["Wallet"])
app.include_router(insurance.router, prefix="/api/v1/insurance", tags=["Insurance"])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policies"])
app.include_router(claims.router, prefix="/api/v1/claims", tags=["Claims"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

from routers import chatbot
app.include_router(chatbot.router, prefix="/api/v1/chat", tags=["Chatbot"])

from routers import simulation
app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["Simulation"])

from routers import monitor
app.include_router(monitor.router, prefix="/api/v1/monitor", tags=["Monitor"])
