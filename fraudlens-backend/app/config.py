"""
FraudLens AI - Configuration Module
Uses Pydantic v2 BaseSettings for type-safe environment configuration.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core Application Settings
    APP_NAME: str = "FraudLens AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "fraudlens-super-secret-production-key-change-in-prod-2026"

    # Security & JWT Settings
    JWT_SECRET_KEY: str = "fraudlens-jwt-secret-key-change-in-production-use-strong-entropy"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    # Defaults to local SQLite if PostgreSQL is not specified
    DATABASE_URL: str = "sqlite:///./fraudlens.db"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # External APIs
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    VIRUSTOTAL_API_KEY: Optional[str] = None
    MCA_API_URL: Optional[str] = None
    MCA_API_KEY: Optional[str] = None
    LINKEDIN_API_URL: Optional[str] = None
    LINKEDIN_API_KEY: Optional[str] = None

    # Storage and File Upload Limits
    UPLOAD_MAX_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["pdf", "png", "jpg", "jpeg", "webp", "csv", "xlsx"]
    )
    TEMP_UPLOAD_DIR: str = "./temp_uploads"
    REPORTS_DIR: str = "./generated_reports"
    DATASETS_DIR: str = "./datasets"
    MODELS_DIR: str = "./models"

    # Rate Limiting
    RATE_LIMIT_AUTH: int = 15
    RATE_LIMIT_SCAM: int = 30
    RATE_LIMIT_UPI: int = 20

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "null"
    ]

settings = Settings()

# Ensure directories exist
os.makedirs(settings.TEMP_UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
os.makedirs(settings.DATASETS_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
