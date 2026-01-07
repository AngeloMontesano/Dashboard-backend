from __future__ import annotations

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env_file_path = Path(os.getenv("ENV_FILE", ".env"))
    model_config = SettingsConfigDict(
        env_file=str(env_file_path) if env_file_path.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = Field(..., description="PostgreSQL DSN")
    ADMIN_API_KEY: str = Field(..., description="Shared secret for X-Admin-Key")

    # JWT
    JWT_SECRET: str = Field(..., description="JWT secret")
    JWT_ALGORITHM: str = Field("HS256", description="JWT algorithm")

    # Token Laufzeiten (nur Konfiguration, keine Hardcodes in Code)
    ACCESS_TOKEN_EXPIRES_MIN: int = Field(15, description="Access Token TTL in Minuten")
    REFRESH_TOKEN_EXPIRES_DAYS: int = Field(30, description="Refresh Token TTL in Tagen")
    REFRESH_TOKEN_GRACE_MIN: int = Field(5, description="Kulanzzeit in Minuten, in der abgelaufene Refresh Tokens noch akzeptiert werden")

    # Umgebung
    ENVIRONMENT: str = Field("prod", pattern="^(dev|prod)$")
    APP_VERSION: str = Field("0.1.0")
    GIT_COMMIT: str = Field("unknown")
    BUILD_TIMESTAMP: str = Field("unknown")
    BUILD_BRANCH: str = Field("unknown")
    IMAGE_TAG: str = Field("unknown")

    # Multi-Tenancy
    BASE_DOMAIN: str = Field(..., description="Base domain für Tenant Subdomains, z.B. test.myitnetwork.de")
    BASE_ADMIN_DOMAIN: str = Field(..., description="Base domain für Admin UI Subdomains")


settings = Settings()
