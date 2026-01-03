from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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

    # Umgebung
    ENVIRONMENT: str = Field("prod", pattern="^(dev|prod)$")
    APP_VERSION: str = Field("0.1.0")
    GIT_COMMIT: str | None = Field(default=None)

    # Multi-Tenancy
    BASE_DOMAIN: str = Field(..., description="Base domain für Tenant Subdomains, z.B. test.myitnetwork.de")
    BASE_ADMIN_DOMAIN: str = Field(..., description="Base domain für Admin UI Subdomains")


settings = Settings()
