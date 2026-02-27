import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.conftest import get_auth_headers
from tests.factories import make_customer_data, make_product_data, make_supplier_data


class TestProductExports:
    @pytest.mark.asyncio
    async def test_export_products(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        # Create a product first
        await client.post("/api/v1/products", headers=headers, json=make_product_data())
        resp = await client.get("/api/v1/products/export", headers=headers)
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers["content-type"]

    @pytest.mark.asyncio
    async def test_download_template(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/products/template", headers=headers)
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers["content-type"]

    @pytest.mark.asyncio
    async def test_import_products(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        # Create a simple Excel file
        from app.utils.excel import create_workbook

        rows = [
            [
                f"SKU-IMP-{uuid.uuid4().hex[:6]}",
                "导入测试",
                "Import Test",
                "candy",
                "TestBrand",
                "100g",
                "0.1",
                "0.001",
                "24/箱",
                "40",
                "30",
                "25",
                "10",
                "365",
            ]
        ]
        headers_list = [
            "sku_code",
            "name_cn",
            "name_en",
            "category",
            "brand",
            "spec",
            "unit_weight_kg",
            "unit_volume_cbm",
            "packing_spec",
            "carton_length_cm",
            "carton_width_cm",
            "carton_height_cm",
            "carton_gross_weight_kg",
            "shelf_life_days",
        ]
        output = create_workbook("导入", headers_list, rows)
        resp = await client.post(
            "/api/v1/products/import",
            headers=headers,
            files={
                "file": (
                    "products.xlsx",
                    output.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["created"] >= 1


class TestCustomerExport:
    @pytest.mark.asyncio
    async def test_export_customers(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        await client.post("/api/v1/customers", headers=headers, json=make_customer_data())
        resp = await client.get("/api/v1/customers/export", headers=headers)
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers["content-type"]


class TestSupplierExport:
    @pytest.mark.asyncio
    async def test_export_suppliers(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        await client.post("/api/v1/suppliers", headers=headers, json=make_supplier_data())
        resp = await client.get("/api/v1/suppliers/export", headers=headers)
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers["content-type"]


class TestSalesOrderExport:
    @pytest.mark.asyncio
    async def test_export_sales_orders(
        self, client: AsyncClient, admin_user: User, db_session: AsyncSession
    ):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/sales-orders/export", headers=headers)
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers["content-type"]


class TestInventoryExport:
    @pytest.mark.asyncio
    async def test_export_inventory(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/warehouse/inventory/export", headers=headers)
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers["content-type"]
