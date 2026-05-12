from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings

app = FastAPI(
    title=settings.APP_TITLE,
    description="AI-Powered Insurance Simulator API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
# Uncomment as each router is implemented:

from routers import auth, wallet, insurance, policies

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["Wallet"])

# from routers import insurance, policies, claims
# from routers import simulation, chatbot, notifications, admin
#
app.include_router(insurance.router, prefix="/api/v1/insurance", tags=["Insurance"])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policies"])
# app.include_router(claims.router, prefix="/api/v1/claims", tags=["Claims"])
# app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["Simulation"])
# app.include_router(chatbot.router, prefix="/api/v1/chat", tags=["Chatbot"])
# app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
# app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
