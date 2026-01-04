from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.security import verify_password
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin-auth"])


class AdminCredentialLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
async def admin_login_with_credentials(
    payload: AdminCredentialLogin,
    db: AsyncSession = Depends(get_db),
) -> dict:
    email = payload.email

    user = await db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "admin_key": settings.ADMIN_API_KEY,
        "actor": user.email,
    }
