import pytest
from httpx import AsyncClient

from app.models.user import User
from tests.conftest import get_auth_headers


class TestStatistics:
    @pytest.mark.asyncio
    async def test_sales_summary_by_month(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/statistics/sales-summary?group_by=month", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert "items" in data["data"]

    @pytest.mark.asyncio
    async def test_sales_summary_by_customer(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(
            "/api/v1/statistics/sales-summary?group_by=customer", headers=headers
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_purchase_summary(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(
            "/api/v1/statistics/purchase-summary?group_by=month", headers=headers
        )
        assert resp.status_code == 200
        assert "items" in resp.json()["data"]

    @pytest.mark.asyncio
    async def test_container_summary(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(
            "/api/v1/statistics/container-summary?group_by=month", headers=headers
        )
        assert resp.status_code == 200
        assert "items" in resp.json()["data"]

    @pytest.mark.asyncio
    async def test_customer_ranking(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/statistics/customer-ranking", headers=headers)
        assert resp.status_code == 200
        assert "items" in resp.json()["data"]

    @pytest.mark.asyncio
    async def test_product_ranking(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/statistics/product-ranking", headers=headers)
        assert resp.status_code == 200
        assert "items" in resp.json()["data"]

    @pytest.mark.asyncio
    async def test_viewer_cannot_access_statistics(self, client: AsyncClient, viewer_user: User):
        headers = get_auth_headers(viewer_user)
        resp = await client.get("/api/v1/statistics/sales-summary", headers=headers)
        assert resp.status_code == 403
