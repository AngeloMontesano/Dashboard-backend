from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import hash_password
from app.models.user import User
from app.modules.admin.schemas import UserCreate, UserOut, UserUpdate
from app.models.audit_log import AdminAuditLog

router = APIRouter(prefix="/users", tags=["admin-users"])

ADMIN_ACTOR = "admin"


def _user_payload_safe(user: User) -> dict:
    """
    Keine Passwörter und keine Hashes.
    """
    return {
        "email": user.email,
        "is_active": user.is_active,
        "has_password": user.password_hash is not None,
    }


@router.get("", response_model=list[UserOut])
async def admin_list_users(db: AsyncSession = Depends(get_db)) -> list[UserOut]:
    result = await db.execute(select(User).order_by(User.email))
    users = list(result.scalars().all())

    return [
        UserOut(
            id=str(u.id),
            email=u.email,
            is_active=u.is_active,
            has_password=u.password_hash is not None,
        )
        for u in users
    ]


@router.post("", response_model=UserOut, status_code=201)
async def admin_create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserOut:
    exists = await db.execute(select(User).where(User.email == payload.email.lower()))
    if exists.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "user_exists", "message": "User already exists"}},
        )

    password_hash: str | None = None
    if payload.password:
        try:
            password_hash = hash_password(payload.password)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail={"error": {"code": "password_invalid", "message": "Invalid password"}},
            )

    user = User(
        email=payload.email.lower(),
        password_hash=password_hash,
        is_active=True,
    )

    db.add(user)
    await db.flush()

    db.add(
        AdminAuditLog(
            actor=ADMIN_ACTOR,
            action="create",
            entity_type="user",
            entity_id=str(user.id),
            payload=_user_payload_safe(user),
        )
    )

    await db.commit()
    await db.refresh(user)

    return UserOut(
        id=str(user.id),
        email=user.email,
        is_active=user.is_active,
        has_password=user.password_hash is not None,
    )


@router.patch("/{user_id}", response_model=UserOut)
async def admin_update_user(user_id: uuid.UUID, payload: UserUpdate, db: AsyncSession = Depends(get_db)) -> UserOut:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "user_not_found", "message": "User not found"}},
        )

    changes: dict = {}

    if payload.is_active is not None and payload.is_active != user.is_active:
        changes["is_active"] = {"from": user.is_active, "to": payload.is_active}
        user.is_active = payload.is_active

    if payload.password is not None:
        try:
            user.password_hash = hash_password(payload.password)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail={"error": {"code": "password_invalid", "message": "Invalid password"}},
            )
        changes["password_reset"] = True

    db.add(
        AdminAuditLog(
            actor=ADMIN_ACTOR,
            action="update",
            entity_type="user",
            entity_id=str(user.id),
            payload={"changes": changes, "user": _user_payload_safe(user)},
        )
    )

    await db.commit()
    await db.refresh(user)

    return UserOut(
        id=str(user.id),
        email=user.email,
        is_active=user.is_active,
        has_password=user.password_hash is not None,
    )
