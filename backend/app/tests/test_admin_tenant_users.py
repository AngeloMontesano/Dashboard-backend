from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from app.main import app


ADMIN_HEADERS = {
    "X-Admin-Key": "change-me",
    "X-Admin-Actor": "test-suite",
}


@pytest.mark.asyncio
async def test_admin_tenant_users_create_list_patch_and_email_unique_globally():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1) Two tenants
        t1 = await client.post(
            "/admin/tenants",
            headers=ADMIN_HEADERS,
            json={"slug": "t1", "name": "Tenant 1"},
        )
        assert t1.status_code == 201, t1.text
        tenant1_id = t1.json()["id"]

        t2 = await client.post(
            "/admin/tenants",
            headers=ADMIN_HEADERS,
            json={"slug": "t2", "name": "Tenant 2"},
        )
        assert t2.status_code == 201, t2.text
        tenant2_id = t2.json()["id"]

        # 2) Create tenant user in tenant 1
        email = "user@example.com"
        create_1 = await client.post(
            f"/admin/tenants/{tenant1_id}/users",
            headers=ADMIN_HEADERS,
            json={
                "email": email,
                "role": "staff",
                "password": "VeryStrongPW123!",
                "user_is_active": True,
                "membership_is_active": True,
            },
        )
        assert create_1.status_code == 201, create_1.text
        u1 = create_1.json()
        assert u1["email"] == email
        assert u1["role"] == "staff"
        assert u1["user_is_active"] is True
        assert u1["membership_is_active"] is True
        assert uuid.UUID(u1["user_id"])
        assert uuid.UUID(u1["membership_id"])

        # 3) Same email in another tenant must reuse same global user_id
        create_2 = await client.post(
            f"/admin/tenants/{tenant2_id}/users",
            headers=ADMIN_HEADERS,
            json={
                "email": email,
                "role": "readonly",
                "password": None,
                "user_is_active": True,
                "membership_is_active": True,
            },
        )
        assert create_2.status_code == 201, create_2.text
        u2 = create_2.json()
        assert u2["email"] == email
        assert u2["role"] == "readonly"
        assert u2["user_id"] == u1["user_id"]  # global uniqueness by email
        assert u2["membership_id"] != u1["membership_id"]

        # 4) Creating same email again in same tenant must fail (membership exists)
        create_dup = await client.post(
            f"/admin/tenants/{tenant1_id}/users",
            headers=ADMIN_HEADERS,
            json={
                "email": email,
                "role": "staff",
                "password": None,
                "user_is_active": True,
                "membership_is_active": True,
            },
        )
        assert create_dup.status_code == 409, create_dup.text

        # 5) List tenant users includes the email
        lst = await client.get(
            f"/admin/tenants/{tenant1_id}/users?limit=50",
            headers=ADMIN_HEADERS,
        )
        assert lst.status_code == 200, lst.text
        emails = [row["email"] for row in lst.json()]
        assert email in emails

        # 6) Patch membership: change role, disable membership, disable user
        patch = await client.patch(
            f"/admin/tenants/{tenant1_id}/users/{u1['membership_id']}",
            headers=ADMIN_HEADERS,
            json={
                "role": "tenant_admin",
                "membership_is_active": False,
                "user_is_active": False,
            },
        )
        assert patch.status_code == 200, patch.text
        patched = patch.json()
        assert patched["membership_id"] == u1["membership_id"]
        assert patched["user_id"] == u1["user_id"]
        assert patched["role"] == "tenant_admin"
        assert patched["membership_is_active"] is False
        assert patched["user_is_active"] is False
