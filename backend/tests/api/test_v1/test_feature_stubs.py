import uuid

import pytest
from httpx import AsyncClient

from app.models.user import User
from tests.conftest import get_auth_headers
from tests.factories import (
    make_customer_data,
    make_product_data,
    make_purchase_order_data,
    make_sales_order_data,
    make_supplier_data,
)


class TestCustomerOrders:
    @pytest.mark.asyncio
    async def test_get_customer_orders(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        # Create customer
        cust_resp = await client.post(
            "/api/v1/customers", headers=headers, json=make_customer_data()
        )
        customer_id = cust_resp.json()["data"]["id"]

        # Create product
        prod_resp = await client.post("/api/v1/products", headers=headers, json=make_product_data())
        product_id = prod_resp.json()["data"]["id"]

        # Create SO for this customer
        so_data = make_sales_order_data(customer_id, product_id)
        await client.post("/api/v1/sales-orders", headers=headers, json=so_data)

        # Get customer orders
        resp = await client.get(f"/api/v1/customers/{customer_id}/orders", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_customer_orders_not_found(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(f"/api/v1/customers/{uuid.uuid4()}/orders", headers=headers)
        assert resp.status_code == 404


class TestSupplierPurchaseOrders:
    @pytest.mark.asyncio
    async def test_get_supplier_purchase_orders(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        # Create supplier
        sup_resp = await client.post(
            "/api/v1/suppliers", headers=headers, json=make_supplier_data()
        )
        supplier_id = sup_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/suppliers/{supplier_id}/purchase-orders", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 0


class TestPurchaseOrderReceivingNotes:
    @pytest.mark.asyncio
    async def test_get_receiving_notes(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        # Create product, supplier, SO, PO
        prod_resp = await client.post("/api/v1/products", headers=headers, json=make_product_data())
        product_id = prod_resp.json()["data"]["id"]

        sup_resp = await client.post(
            "/api/v1/suppliers", headers=headers, json=make_supplier_data()
        )
        supplier_id = sup_resp.json()["data"]["id"]

        po_data = make_purchase_order_data(supplier_id, product_id)
        po_resp = await client.post("/api/v1/purchase-orders", headers=headers, json=po_data)
        po_id = po_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/purchase-orders/{po_id}/receiving-notes", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 0


class TestGeneratePurchaseOrders:
    @pytest.mark.asyncio
    async def test_generate_purchase_for_so_without_supplier(
        self, client: AsyncClient, admin_user: User
    ):
        headers = get_auth_headers(admin_user)
        # Create customer, product (no default supplier)
        cust_resp = await client.post(
            "/api/v1/customers", headers=headers, json=make_customer_data()
        )
        customer_id = cust_resp.json()["data"]["id"]

        prod_resp = await client.post("/api/v1/products", headers=headers, json=make_product_data())
        product_id = prod_resp.json()["data"]["id"]

        # Create SO
        so_data = make_sales_order_data(customer_id, product_id)
        so_resp = await client.post("/api/v1/sales-orders", headers=headers, json=so_data)
        so_id = so_resp.json()["data"]["id"]

        # Generate purchase orders (should return 0 since no default supplier)
        resp = await client.post(f"/api/v1/sales-orders/{so_id}/generate-purchase", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["count"] == 0


class TestFulfillment:
    @pytest.mark.asyncio
    async def test_get_fulfillment(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        # Create customer, product, SO
        cust_resp = await client.post(
            "/api/v1/customers", headers=headers, json=make_customer_data()
        )
        customer_id = cust_resp.json()["data"]["id"]

        prod_resp = await client.post("/api/v1/products", headers=headers, json=make_product_data())
        product_id = prod_resp.json()["data"]["id"]

        so_data = make_sales_order_data(customer_id, product_id)
        so_resp = await client.post("/api/v1/sales-orders", headers=headers, json=so_data)
        so_id = so_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/sales-orders/{so_id}/fulfillment", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["sales_order_id"] == so_id
        assert "purchase_orders" in data
        assert "receiving_notes" in data
        assert "inventory" in data
        assert "containers" in data
        assert "logistics" in data

    @pytest.mark.asyncio
    async def test_get_fulfillment_not_found(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(f"/api/v1/sales-orders/{uuid.uuid4()}/fulfillment", headers=headers)
        assert resp.status_code == 404
