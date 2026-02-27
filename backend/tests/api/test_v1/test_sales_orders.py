import uuid

import pytest
from httpx import AsyncClient

from app.models.user import User
from tests.conftest import get_auth_headers
from tests.factories import make_customer_data, make_product_data, make_sales_order_data


@pytest.fixture
async def seed_customer(client: AsyncClient, admin_user: User) -> str:
    """Create a customer and return its id."""
    headers = get_auth_headers(admin_user)
    resp = await client.post("/api/v1/customers", json=make_customer_data(), headers=headers)
    return resp.json()["data"]["id"]


@pytest.fixture
async def seed_product(client: AsyncClient, admin_user: User) -> str:
    """Create a product and return its id."""
    headers = get_auth_headers(admin_user)
    resp = await client.post("/api/v1/products", json=make_product_data(), headers=headers)
    return resp.json()["data"]["id"]


class TestCreateSalesOrder:
    async def test_create_success(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        data = make_sales_order_data(seed_customer, seed_product)
        resp = await client.post("/api/v1/sales-orders", json=data, headers=headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["order_no"].startswith("SO-")
        assert body["data"]["status"] == "draft"
        assert len(body["data"]["items"]) == 1
        assert body["data"]["total_quantity"] == 100

    async def test_create_multiple_items(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        data = make_sales_order_data(seed_customer, seed_product)
        # Add a second item (same product, different qty)
        data["items"].append(
            {
                "product_id": seed_product,
                "quantity": 200,
                "unit": "carton",
                "unit_price": "30.00",
            }
        )
        resp = await client.post("/api/v1/sales-orders", json=data, headers=headers)
        assert resp.status_code == 201
        assert len(resp.json()["data"]["items"]) == 2
        assert resp.json()["data"]["total_quantity"] == 300

    async def test_create_no_items_fails(
        self, client: AsyncClient, admin_user: User, seed_customer: str
    ):
        headers = get_auth_headers(admin_user)
        data = {
            "customer_id": seed_customer,
            "order_date": "2026-02-27",
            "destination_port": "Bangkok",
            "trade_term": "FOB",
            "currency": "USD",
            "payment_method": "TT",
            "items": [],
        }
        resp = await client.post("/api/v1/sales-orders", json=data, headers=headers)
        assert resp.status_code == 422

    async def test_create_no_auth(self, client: AsyncClient, seed_customer: str, seed_product: str):
        data = make_sales_order_data(seed_customer, seed_product)
        resp = await client.post("/api/v1/sales-orders", json=data)
        assert resp.status_code in (401, 403)

    async def test_create_viewer_forbidden(
        self, client: AsyncClient, viewer_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(viewer_user)
        data = make_sales_order_data(seed_customer, seed_product)
        resp = await client.post("/api/v1/sales-orders", json=data, headers=headers)
        assert resp.status_code == 403


class TestListSalesOrders:
    async def test_list(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=headers,
        )
        resp = await client.get("/api/v1/sales-orders", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 1

    async def test_list_filter_by_status(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=headers,
        )
        resp = await client.get("/api/v1/sales-orders?status=draft", headers=headers)
        assert resp.status_code == 200
        for item in resp.json()["data"]["items"]:
            assert item["status"] == "draft"

    async def test_list_filter_by_customer(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=headers,
        )
        resp = await client.get(
            f"/api/v1/sales-orders?customer_id={seed_customer}", headers=headers
        )
        assert resp.status_code == 200
        for item in resp.json()["data"]["items"]:
            assert item["customer_id"] == seed_customer


class TestGetSalesOrder:
    async def test_get_with_items(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=headers,
        )
        order_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/sales-orders/{order_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == order_id
        assert len(resp.json()["data"]["items"]) == 1

    async def test_get_not_found(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(f"/api/v1/sales-orders/{uuid.uuid4()}", headers=headers)
        assert resp.status_code == 404


class TestUpdateSalesOrder:
    async def test_update_header(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=headers,
        )
        order_id = create_resp.json()["data"]["id"]

        resp = await client.put(
            f"/api/v1/sales-orders/{order_id}",
            json={"destination_port": "Shanghai Port"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["destination_port"] == "Shanghai Port"

    async def test_update_replace_items(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=headers,
        )
        order_id = create_resp.json()["data"]["id"]

        resp = await client.put(
            f"/api/v1/sales-orders/{order_id}",
            json={
                "items": [
                    {
                        "product_id": seed_product,
                        "quantity": 200,
                        "unit": "carton",
                        "unit_price": "30.00",
                    },
                ]
            },
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["total_quantity"] == 200

    async def test_update_non_draft_forbidden(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=headers,
        )
        order_id = create_resp.json()["data"]["id"]

        # Confirm it (moves to purchasing)
        await client.post(f"/api/v1/sales-orders/{order_id}/confirm", headers=headers)

        # Then advance to goods_ready via admin status update
        await client.patch(
            f"/api/v1/sales-orders/{order_id}/status",
            json={"status": "goods_ready"},
            headers=headers,
        )

        # Try to update — should fail (goods_ready not editable)
        resp = await client.put(
            f"/api/v1/sales-orders/{order_id}",
            json={"destination_port": "New Port"},
            headers=headers,
        )
        assert resp.status_code == 422


class TestConfirmSalesOrder:
    async def test_confirm_r10(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        """R10: confirm should set status directly to purchasing."""
        headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=headers,
        )
        order_id = create_resp.json()["data"]["id"]

        resp = await client.post(f"/api/v1/sales-orders/{order_id}/confirm", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "purchasing"

    async def test_confirm_non_draft_fails(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=headers,
        )
        order_id = create_resp.json()["data"]["id"]
        await client.post(f"/api/v1/sales-orders/{order_id}/confirm", headers=headers)

        # Try again — should fail
        resp = await client.post(f"/api/v1/sales-orders/{order_id}/confirm", headers=headers)
        assert resp.status_code == 422

    async def test_confirm_viewer_forbidden(
        self,
        client: AsyncClient,
        viewer_user: User,
        admin_user: User,
        seed_customer: str,
        seed_product: str,
    ):
        admin_headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=admin_headers,
        )
        order_id = create_resp.json()["data"]["id"]

        viewer_headers = get_auth_headers(viewer_user)
        resp = await client.post(f"/api/v1/sales-orders/{order_id}/confirm", headers=viewer_headers)
        assert resp.status_code == 403


class TestKanban:
    async def test_kanban(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=headers,
        )
        resp = await client.get("/api/v1/sales-orders/kanban", headers=headers)
        assert resp.status_code == 200
        assert "items" in resp.json()["data"]


class TestStatusUpdate:
    async def test_admin_status_change(
        self, client: AsyncClient, admin_user: User, seed_customer: str, seed_product: str
    ):
        headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=headers,
        )
        order_id = create_resp.json()["data"]["id"]

        # Confirm first
        await client.post(f"/api/v1/sales-orders/{order_id}/confirm", headers=headers)

        # Admin can manually change status
        resp = await client.patch(
            f"/api/v1/sales-orders/{order_id}/status",
            json={"status": "goods_ready"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "goods_ready"

    async def test_non_admin_status_change_forbidden(
        self,
        client: AsyncClient,
        viewer_user: User,
        admin_user: User,
        seed_customer: str,
        seed_product: str,
    ):
        admin_headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/sales-orders",
            json=make_sales_order_data(seed_customer, seed_product),
            headers=admin_headers,
        )
        order_id = create_resp.json()["data"]["id"]

        viewer_headers = get_auth_headers(viewer_user)
        resp = await client.patch(
            f"/api/v1/sales-orders/{order_id}/status",
            json={"status": "purchasing"},
            headers=viewer_headers,
        )
        assert resp.status_code == 403
