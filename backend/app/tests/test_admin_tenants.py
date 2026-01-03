from __future__ import annotations

import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)


def _admin_headers(actor: str = "test"):
    return {
        "X-Admin-Key": settings.ADMIN_API_KEY,
        "X-Admin-Actor": actor,
        "Content-Type": "application/json",
    }


def test_admin_health_db_ok():
    r = client.get("/health/db")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "ok"


def test_admin_create_list_delete_tenant_confirm_required():
    slug = f"t{uuid.uuid4().hex[:8]}"
    r_create = client.post(
        "/admin/tenants",
        headers=_admin_headers("pytest"),
        json={"slug": slug, "name": "Pytest Tenant"},
    )
    assert r_create.status_code == 201, r_create.text
    tenant_id = r_create.json()["id"]

    r_list = client.get("/admin/tenants?limit=50", headers=_admin_headers("pytest"))
    assert r_list.status_code == 200, r_list.text
    assert any(t["id"] == tenant_id for t in r_list.json())

    r_del_no_confirm = client.delete(f"/admin/tenants/{tenant_id}", headers=_admin_headers("pytest"))
    assert r_del_no_confirm.status_code == 409

    r_del_confirm = client.delete(f"/admin/tenants/{tenant_id}?confirm=true", headers=_admin_headers("pytest"))
    assert r_del_confirm.status_code == 204
