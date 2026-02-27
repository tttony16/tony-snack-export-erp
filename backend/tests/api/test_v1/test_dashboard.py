import pytest
from httpx import AsyncClient

from app.models.user import User
from tests.conftest import get_auth_headers


class TestDashboard:
    @pytest.mark.asyncio
    async def test_overview(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/dashboard/overview", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert "sales_orders" in data["data"]
        assert "purchase_orders" in data["data"]

    @pytest.mark.asyncio
    async def test_todos(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/dashboard/todos", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "draft_sales_orders" in data
        assert "ordered_purchase_orders" in data
        assert "goods_ready_sales_orders" in data
        assert "arriving_soon_containers" in data

    @pytest.mark.asyncio
    async def test_in_transit(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/dashboard/in-transit", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_expiry_warnings(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/dashboard/expiry-warnings", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "threshold" in data
        assert "items" in data

    @pytest.mark.asyncio
    async def test_viewer_can_access_dashboard(self, client: AsyncClient, viewer_user: User):
        headers = get_auth_headers(viewer_user)
        resp = await client.get("/api/v1/dashboard/overview", headers=headers)
        assert resp.status_code == 200
