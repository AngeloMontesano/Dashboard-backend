from __future__ import annotations

import uuid


from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership
from app.models.tenant import Tenant
from app.models.user import User
from app.modules.admin.schemas import TenantUserOut
from app.modules.admin.audit import write_audit_log

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.core.security import hash_password

ALLOWED_ROLES = {"tenant_admin", "staff", "readonly"}

async def list_tenants(
    db: AsyncSession,
    q: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Tenant]:
    """
    Listet Tenants.
    Optional mit Suche (case insensitive) auf slug und name.
    """
    stmt = select(Tenant)

    if q:
        query = q.strip()
        if query:
            like = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Tenant.slug.ilike(like),
                    Tenant.name.ilike(like),
                )
            )

    stmt = stmt.order_by(Tenant.slug.asc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_tenant(db: AsyncSession, actor: str, slug: str, name: str) -> Tenant:
    """
    Legt einen neuen Tenant an und schreibt Audit.
    """
    tenant = Tenant(slug=slug.lower(), name=name, is_active=True)
    db.add(tenant)
    await db.flush()

    await write_audit_log(
        db=db,
        actor=actor,
        action="create",
        entity_type="tenant",
        entity_id=str(tenant.id),
        payload={"slug": tenant.slug, "name": tenant.name, "is_active": tenant.is_active},
    )

    await db.commit()
    await db.refresh(tenant)
    return tenant


async def update_tenant(
    db: AsyncSession,
    actor: str,
    tenant: Tenant,
    name: str | None,
    is_active: bool | None,
) -> Tenant:
    """
    Aktualisiert Tenant Felder und schreibt Audit.
    """
    changes: dict = {}

    if name is not None and name != tenant.name:
        changes["name"] = {"from": tenant.name, "to": name}
        tenant.name = name

    if is_active is not None and is_active != tenant.is_active:
        changes["is_active"] = {"from": tenant.is_active, "to": is_active}
        tenant.is_active = is_active

    await write_audit_log(
        db=db,
        actor=actor,
        action="update",
        entity_type="tenant",
        entity_id=str(tenant.id),
        payload={"changes": changes},
    )

    await db.commit()
    await db.refresh(tenant)
    return tenant


async def delete_tenant(db: AsyncSession, *, actor: str, tenant: Tenant) -> None:
    """
    Löscht einen Tenant.
    Regel: nur erlaubt, wenn keine Memberships existieren.
    """
    exists_stmt = (
        select(Membership.id)
        .where(Membership.tenant_id == tenant.id)
        .limit(1)
    )
    res = await db.execute(exists_stmt)
    if res.scalar_one_or_none() is not None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "tenant_has_memberships",
                    "message": "Tenant cannot be deleted while memberships exist",
                }
            },
        )

    payload = {
        "id": str(tenant.id),
        "slug": tenant.slug,
        "name": tenant.name,
        "is_active": bool(tenant.is_active),
    }

    await db.delete(tenant)

    await write_audit_log(
        db=db,
        actor=actor,
        action="delete",
        entity_type="tenant",
        entity_id=str(tenant.id),
        payload=payload,
    )

    await db.commit()



async def list_tenant_users(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    q: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[TenantUserOut]:
    """
    Alle User für einen Tenant inkl. Membership Daten.
    Optional Suche auf Email (case insensitive).
    """
    stmt = (
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(Membership.tenant_id == tenant_id)
    )

    if q:
        query = q.strip()
        if query:
            stmt = stmt.where(User.email.ilike(f"%{query}%"))

    stmt = stmt.order_by(User.email.asc()).limit(limit).offset(offset)

    res = await db.execute(stmt)
    rows = res.all()

    out: list[TenantUserOut] = []
    for m, u in rows:
        out.append(
            TenantUserOut(
                membership_id=str(m.id),
                user_id=str(u.id),
                email=u.email,
                role=m.role,
                user_is_active=bool(u.is_active),
                membership_is_active=bool(m.is_active),
            )
        )
    return out


async def create_tenant_user(
    db: AsyncSession,
    *,
    actor: str,
    tenant: Tenant,
    email: str,
    role: str,
    password: str | None,
    user_is_active: bool,
    membership_is_active: bool,
) -> TenantUserOut:
    """
    Upsert User by email, dann Membership im Tenant anlegen.
    Email ist global eindeutig.
    """
    if role not in ALLOWED_ROLES:
        raise ValueError("invalid_role")

    normalized_email = email.strip().lower()

    user_stmt = select(User).where(User.email == normalized_email)
    user_res = await db.execute(user_stmt)
    user = user_res.scalar_one_or_none()

    created_user = False
    if user is None:
        user = User(
            email=normalized_email,
            is_active=bool(user_is_active),
            password_hash=hash_password(password) if password else None,
        )
        db.add(user)
        await db.flush()
        created_user = True
    else:
        # optional: im Create Call User aktiv setzen, wenn mitgegeben
        if user_is_active is not None:
            user.is_active = bool(user_is_active)
        # optional Passwort setzen
        if password:
            user.password_hash = hash_password(password)

    # prüfen ob Membership schon existiert
    m_stmt = select(Membership).where(
        Membership.tenant_id == tenant.id,
        Membership.user_id == user.id,
    )
    m_res = await db.execute(m_stmt)
    membership = m_res.scalar_one_or_none()
    if membership is not None:
        # Membership existiert, wir können Rolle oder Flags nicht still überschreiben
        # Admin soll dafür PATCH nutzen
        raise ValueError("membership_exists")

    membership = Membership(
        tenant_id=tenant.id,
        user_id=user.id,
        role=role,
        is_active=bool(membership_is_active),
    )
    db.add(membership)
    await db.flush()

    await write_audit_log(
        db=db,
        actor=actor,
        action="create",
        entity_type="tenant_user",
        entity_id=str(membership.id),
        payload={
            "tenant_id": str(tenant.id),
            "user_id": str(user.id),
            "email": normalized_email,
            "role": role,
            "user_created": created_user,
            "user_is_active": bool(user.is_active),
            "membership_is_active": bool(membership.is_active),
        },
    )

    await db.commit()
    return TenantUserOut(
        membership_id=str(membership.id),
        user_id=str(user.id),
        email=user.email,
        role=membership.role,
        user_is_active=bool(user.is_active),
        membership_is_active=bool(membership.is_active),
    )


async def update_tenant_user(
    db: AsyncSession,
    *,
    actor: str,
    tenant_id: uuid.UUID,
    membership_id: uuid.UUID,
    role: str | None,
    password: str | None,
    user_is_active: bool | None,
    membership_is_active: bool | None,
) -> TenantUserOut:
    """
    Patch: Membership und User Flags sowie Passwort.
    """
    stmt = (
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(Membership.id == membership_id)
        .where(Membership.tenant_id == tenant_id)
    )
    res = await db.execute(stmt)
    row = res.first()
    if row is None:
        raise ValueError("tenant_user_not_found")

    membership, user = row
    changes: dict = {}

    if role is not None:
        if role not in ALLOWED_ROLES:
            raise ValueError("invalid_role")
        if role != membership.role:
            changes["role"] = {"from": membership.role, "to": role}
            membership.role = role

    if membership_is_active is not None and bool(membership_is_active) != bool(membership.is_active):
        changes["membership_is_active"] = {"from": bool(membership.is_active), "to": bool(membership_is_active)}
        membership.is_active = bool(membership_is_active)

    if user_is_active is not None and bool(user_is_active) != bool(user.is_active):
        changes["user_is_active"] = {"from": bool(user.is_active), "to": bool(user_is_active)}
        user.is_active = bool(user_is_active)

    if password is not None:
        # Passwort setzen oder bewusst entfernen, je nach Policy.
        # Ich setze: leere Strings sind invalid, None bedeutet "nicht ändern".
        if password.strip() == "":
            raise ValueError("invalid_password")
        user.password_hash = hash_password(password)
        changes["password_set"] = True

    await write_audit_log(
        db=db,
        actor=actor,
        action="update",
        entity_type="tenant_user",
        entity_id=str(membership.id),
        payload={"tenant_id": str(tenant_id), "changes": changes},
    )

    await db.commit()

    return TenantUserOut(
        membership_id=str(membership.id),
        user_id=str(user.id),
        email=user.email,
        role=membership.role,
        user_is_active=bool(user.is_active),
        membership_is_active=bool(membership.is_active),
    )


async def delete_tenant_user(
    db: AsyncSession,
    *,
    actor: str,
    tenant_id: uuid.UUID,
    membership_id: uuid.UUID,
) -> None:
    """
    Löscht eine Membership (User bleibt erhalten, da global eindeutig).
    """
    stmt = (
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(Membership.id == membership_id)
        .where(Membership.tenant_id == tenant_id)
    )
    res = await db.execute(stmt)
    row = res.first()
    if row is None:
        raise ValueError("tenant_user_not_found")

    membership, user = row

    await db.delete(membership)

    await write_audit_log(
        db=db,
        actor=actor,
        action="delete",
        entity_type="tenant_user",
        entity_id=str(membership.id),
        payload={
            "tenant_id": str(tenant_id),
            "user_id": str(user.id),
            "email": user.email,
        },
    )

    await db.commit()


async def create_membership(
    db: AsyncSession,
    actor: str,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    role: str,
) -> Membership:
    """
    Legt eine Membership an und schreibt Audit.
    Regel: pro Tenant nur eine Membership pro User.
    """
    if role not in ALLOWED_ROLES:
        raise ValueError("invalid_role")

    # 1 User = 1 Membership pro Tenant erzwingen
    exists_stmt = (
        select(Membership.id)
        .where(Membership.user_id == user_id, Membership.tenant_id == tenant_id)
        .limit(1)
    )
    res = await db.execute(exists_stmt)
    if res.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "user_already_assigned",
                    "message": "User already has a membership for this tenant",
                }
            },
        )

    membership = Membership(
        user_id=user_id,
        tenant_id=tenant_id,
        role=role,
        is_active=True,
    )
    db.add(membership)
    await db.flush()

    await write_audit_log(
        db=db,
        actor=actor,
        action="create",
        entity_type="membership",
        entity_id=str(membership.id),
        payload={
            "user_id": str(membership.user_id),
            "tenant_id": str(membership.tenant_id),
            "role": membership.role,
            "is_active": membership.is_active,
        },
    )

    await db.commit()
    await db.refresh(membership)
    return membership

async def update_membership(
    db: AsyncSession,
    actor: str,
    membership: Membership,
    role: str | None,
    is_active: bool | None,
) -> Membership:
    """
    Aktualisiert Membership und schreibt Audit.
    """
    changes: dict = {}

    if role is not None:
        if role not in ALLOWED_ROLES:
            raise ValueError("invalid_role")
        if role != membership.role:
            changes["role"] = {"from": membership.role, "to": role}
        membership.role = role

    if is_active is not None and is_active != membership.is_active:
        changes["is_active"] = {"from": membership.is_active, "to": is_active}
        membership.is_active = is_active

    await write_audit_log(
        db=db,
        actor=actor,
        action="update",
        entity_type="membership",
        entity_id=str(membership.id),
        payload={"changes": changes},
    )

    await db.commit()
    await db.refresh(membership)
    return membership


async def create_user(db, payload):
    email = normalize_email(payload.email)

    user = User(
        email=email,
        password_hash=hash_password(payload.password) if payload.password else None,
        is_active=True,
    )

    try:
        db.add(user)
        await db.flush()
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "user_exists",
                    "message": "User already exists",
                }
            },
        )

    return user
