import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.conftest import get_auth_headers


class TestSystemUsers:
    @pytest.mark.asyncio
    async def test_list_users(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/system/users", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["total"] >= 1

    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.post(
            "/api/v1/system/users",
            headers=headers,
            json={
                "username": f"newuser_{uuid.uuid4().hex[:8]}",
                "password": "password123",
                "display_name": "New User",
                "role": "viewer",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["role"] == "viewer"

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        username = f"dupuser_{uuid.uuid4().hex[:8]}"
        await client.post(
            "/api/v1/system/users",
            headers=headers,
            json={
                "username": username,
                "password": "password123",
                "display_name": "Dup User",
            },
        )
        resp = await client.post(
            "/api/v1/system/users",
            headers=headers,
            json={
                "username": username,
                "password": "password123",
                "display_name": "Dup User 2",
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_get_user(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(f"/api/v1/system/users/{admin_user.id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["username"] == admin_user.username

    @pytest.mark.asyncio
    async def test_update_user(
        self, client: AsyncClient, admin_user: User, db_session: AsyncSession
    ):
        headers = get_auth_headers(admin_user)
        # Create a user to update
        resp = await client.post(
            "/api/v1/system/users",
            headers=headers,
            json={
                "username": f"upd_{uuid.uuid4().hex[:8]}",
                "password": "password123",
                "display_name": "To Update",
            },
        )
        user_id = resp.json()["data"]["id"]
        resp = await client.put(
            f"/api/v1/system/users/{user_id}",
            headers=headers,
            json={"display_name": "Updated Name"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["display_name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_user_role(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.post(
            "/api/v1/system/users",
            headers=headers,
            json={
                "username": f"role_{uuid.uuid4().hex[:8]}",
                "password": "password123",
                "display_name": "Role Test",
                "role": "viewer",
            },
        )
        user_id = resp.json()["data"]["id"]
        resp = await client.patch(
            f"/api/v1/system/users/{user_id}/role",
            headers=headers,
            json={"role": "sales"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["role"] == "sales"

    @pytest.mark.asyncio
    async def test_update_user_status(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.post(
            "/api/v1/system/users",
            headers=headers,
            json={
                "username": f"stat_{uuid.uuid4().hex[:8]}",
                "password": "password123",
                "display_name": "Status Test",
            },
        )
        user_id = resp.json()["data"]["id"]
        resp = await client.patch(
            f"/api/v1/system/users/{user_id}/status",
            headers=headers,
            json={"is_active": False},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_active"] is False

    @pytest.mark.asyncio
    async def test_viewer_cannot_manage_users(self, client: AsyncClient, viewer_user: User):
        headers = get_auth_headers(viewer_user)
        resp = await client.get("/api/v1/system/users", headers=headers)
        assert resp.status_code == 403


class TestAuditLogs:
    @pytest.mark.asyncio
    async def test_list_audit_logs(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/system/audit-logs", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    @pytest.mark.asyncio
    async def test_viewer_cannot_view_audit_logs(self, client: AsyncClient, viewer_user: User):
        headers = get_auth_headers(viewer_user)
        resp = await client.get("/api/v1/system/audit-logs", headers=headers)
        assert resp.status_code == 403


class TestSystemConfigs:
    @pytest.mark.asyncio
    async def test_list_configs(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/system/configs", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    @pytest.mark.asyncio
    async def test_update_config(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.put(
            "/api/v1/system/configs/shelf_life_threshold",
            headers=headers,
            json={"config_value": 0.75, "description": "Updated threshold"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["config_key"] == "shelf_life_threshold"
