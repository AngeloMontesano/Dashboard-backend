# app/modules/auth/schemas.py
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    # Dev-Seed nutzt aktuell ein 5-stelliges Passwort ("admin").
    # Wir erlauben bewusst kürzere Passwörter, validieren die Stärke später.
    password: str = Field(min_length=4, max_length=200)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str
    tenant_id: str
    user_id: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
