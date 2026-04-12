from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_TITLE: str = "Insurance Simulator"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/insurance_simulator_db"

    # JWT
    JWT_SECRET_KEY: str = "super-secret-dev-key"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # frontend-user
        "http://localhost:5174",  # frontend-admin
    ]

    # External APIs
    GEMINI_API_KEY: str = ""
    OPENWEATHERMAP_API_KEY: str = ""
    AVIATIONSTACK_API_KEY: str = ""

    # Trigger monitor
    TRIGGER_CHECK_INTERVAL_MINUTES: int = 15

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
