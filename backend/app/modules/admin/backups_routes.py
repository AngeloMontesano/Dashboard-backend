from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/backups", tags=["admin-backups"])


class BackupActionResponse(BaseModel):
    ok: bool
    message: str


@router.post("/tenants/{tenant_id}", response_model=BackupActionResponse)
async def trigger_tenant_backup(tenant_id: uuid.UUID) -> BackupActionResponse:
    """
    Platzhalter Endpoint für Backups. Die konkrete Implementierung folgt später.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Backup for tenant {tenant_id} is not implemented yet.",
    )
