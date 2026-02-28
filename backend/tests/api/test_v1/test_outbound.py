import uuid
from datetime import date

import pytest
from httpx import AsyncClient

from app.models.enums import InspectionResult, UnitType
from app.models.user import User
from tests.conftest import get_auth_headers
from tests.factories import (
    make_container_plan_data,
    make_customer_data,
    make_product_data,
    make_purchase_order_data,
    make_receiving_note_data,
    make_sales_order_data,
    make_supplier_data,
)


@pytest.fixture
async def seed_loaded_plan(client: AsyncClient, admin_user: User) -> dict:
    """Create a container plan in LOADED status via the full chain:
    SO → PO → Receiving → inventory → Container plan → add item → confirm → stuffing → loaded.
    """
    headers = get_auth_headers(admin_user)

    # Create base entities
    cust_resp = await client.post("/api/v1/customers", json=make_customer_data(), headers=headers)
    customer_id = cust_resp.json()["data"]["id"]

    prod_resp = await client.post("/api/v1/products", json=make_product_data(), headers=headers)
    product_id = prod_resp.json()["data"]["id"]

    sup_resp = await client.post("/api/v1/suppliers", json=make_supplier_data(), headers=headers)
    supplier_id = sup_resp.json()["data"]["id"]

    # Create SO and confirm
    so_data = make_sales_order_data(customer_id, product_id)
    so_resp = await client.post("/api/v1/sales-orders", json=so_data, headers=headers)
    so_id = so_resp.json()["data"]["id"]
    so_item_id = so_resp.json()["data"]["items"][0]["id"]
    await client.post(f"/api/v1/sales-orders/{so_id}/confirm", headers=headers)

    # Create PO linked to SO and confirm
    po_data = make_purchase_order_data(
        supplier_id,
        product_id,
        sales_order_ids=[so_id],
        items=[
            {
                "product_id": product_id,
                "sales_order_item_id": so_item_id,
                "quantity": 100,
                "unit": UnitType.CARTON.value,
                "unit_price": "20.00",
            }
        ],
    )
    po_resp = await client.post("/api/v1/purchase-orders", json=po_data, headers=headers)
    po_id = po_resp.json()["data"]["id"]
    po_item_id = po_resp.json()["data"]["items"][0]["id"]
    await client.post(f"/api/v1/purchase-orders/{po_id}/confirm", headers=headers)

    # Receive goods → creates inventory records
    rcv_data = make_receiving_note_data(
        po_id,
        po_item_id,
        product_id,
        items=[
            {
                "purchase_order_item_id": po_item_id,
                "product_id": product_id,
                "expected_quantity": 100,
                "actual_quantity": 100,
                "inspection_result": InspectionResult.PASSED.value,
                "failed_quantity": 0,
                "production_date": date.today().isoformat(),
            }
        ],
    )
    await client.post("/api/v1/warehouse/receiving-notes", json=rcv_data, headers=headers)

    # Create container plan with SO
    plan_data = make_container_plan_data([so_id])
    plan_resp = await client.post("/api/v1/containers", json=plan_data, headers=headers)
    plan_id = plan_resp.json()["data"]["id"]

    # Get inventory batch for batch-driven allocation
    batch_resp = await client.get("/api/v1/warehouse/inventory/batches", headers=headers)
    batches = batch_resp.json()["data"]
    batch = next(b for b in batches if b["product_id"] == product_id)

    # Add item using batch-driven mode (inventory_record_id)
    item_data = {
        "container_seq": 1,
        "inventory_record_id": batch["id"],
        "quantity": 50,
        "volume_cbm": "1.5",
        "weight_kg": "500.0",
    }
    await client.post(f"/api/v1/containers/{plan_id}/items", json=item_data, headers=headers)

    # Confirm plan (locks inventory)
    await client.post(f"/api/v1/containers/{plan_id}/confirm", headers=headers)

    # Record stuffing (plan becomes LOADED)
    stuffing_data = {
        "container_seq": 1,
        "container_no": "CSLU1234567",
        "seal_no": "SL123456",
        "stuffing_date": date.today().isoformat(),
        "stuffing_location": "Shanghai Warehouse",
    }
    await client.post(f"/api/v1/containers/{plan_id}/stuffing", json=stuffing_data, headers=headers)

    return {
        "plan_id": plan_id,
        "so_id": so_id,
        "product_id": product_id,
    }


class TestCreateOutboundOrder:
    async def test_create_success(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        headers = get_auth_headers(admin_user)
        data = {"container_plan_id": seed_loaded_plan["plan_id"]}
        resp = await client.post("/api/v1/outbound-orders", json=data, headers=headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["order_no"].startswith("OUT-")
        assert body["data"]["status"] == "draft"
        assert len(body["data"]["items"]) >= 1

    async def test_create_duplicate_fails(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        """Cannot create two outbound orders for the same container plan."""
        headers = get_auth_headers(admin_user)
        data = {"container_plan_id": seed_loaded_plan["plan_id"]}
        # First creation
        resp1 = await client.post("/api/v1/outbound-orders", json=data, headers=headers)
        assert resp1.status_code == 201

        # Second creation should fail
        resp2 = await client.post("/api/v1/outbound-orders", json=data, headers=headers)
        assert resp2.status_code == 422

    async def test_create_non_loaded_plan_fails(
        self, client: AsyncClient, admin_user: User
    ):
        """Only LOADED plans can create outbound orders."""
        headers = get_auth_headers(admin_user)

        # Create a plan that's in PLANNING status (not loaded)
        cust_resp = await client.post("/api/v1/customers", json=make_customer_data(), headers=headers)
        prod_resp = await client.post("/api/v1/products", json=make_product_data(), headers=headers)

        plan_data = make_container_plan_data(
            destination_port="Bangkok Port",
        )
        plan_resp = await client.post("/api/v1/containers", json=plan_data, headers=headers)
        plan_id = plan_resp.json()["data"]["id"]

        data = {"container_plan_id": plan_id}
        resp = await client.post("/api/v1/outbound-orders", json=data, headers=headers)
        assert resp.status_code == 422

    async def test_create_no_auth(self, client: AsyncClient, seed_loaded_plan: dict):
        data = {"container_plan_id": seed_loaded_plan["plan_id"]}
        resp = await client.post("/api/v1/outbound-orders", json=data)
        assert resp.status_code in (401, 403)

    async def test_create_viewer_forbidden(
        self, client: AsyncClient, viewer_user: User, seed_loaded_plan: dict
    ):
        headers = get_auth_headers(viewer_user)
        data = {"container_plan_id": seed_loaded_plan["plan_id"]}
        resp = await client.post("/api/v1/outbound-orders", json=data, headers=headers)
        assert resp.status_code == 403


class TestListOutboundOrders:
    async def test_list(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        headers = get_auth_headers(admin_user)
        # Create an outbound order first
        data = {"container_plan_id": seed_loaded_plan["plan_id"]}
        await client.post("/api/v1/outbound-orders", json=data, headers=headers)

        resp = await client.get("/api/v1/outbound-orders", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 1


class TestGetOutboundOrder:
    async def test_get(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        headers = get_auth_headers(admin_user)
        data = {"container_plan_id": seed_loaded_plan["plan_id"]}
        create_resp = await client.post("/api/v1/outbound-orders", json=data, headers=headers)
        order_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/outbound-orders/{order_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == order_id

    async def test_get_not_found(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(f"/api/v1/outbound-orders/{uuid.uuid4()}", headers=headers)
        assert resp.status_code == 404


class TestConfirmOutboundOrder:
    async def test_confirm_success(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        headers = get_auth_headers(admin_user)
        # Create outbound order
        data = {"container_plan_id": seed_loaded_plan["plan_id"]}
        create_resp = await client.post("/api/v1/outbound-orders", json=data, headers=headers)
        order_id = create_resp.json()["data"]["id"]

        # Confirm
        confirm_data = {
            "outbound_date": date.today().isoformat(),
            "operator": "Test Operator",
        }
        resp = await client.post(
            f"/api/v1/outbound-orders/{order_id}/confirm",
            json=confirm_data,
            headers=headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["status"] == "confirmed"
        assert body["data"]["operator"] == "Test Operator"

    async def test_confirm_deducts_inventory(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        """Confirming outbound should deduct inventory quantities."""
        headers = get_auth_headers(admin_user)

        # Check inventory before
        inv_resp = await client.get("/api/v1/warehouse/inventory", headers=headers)
        inv_before = inv_resp.json()["data"]["items"]
        product_inv = next(
            (i for i in inv_before if i["product_id"] == seed_loaded_plan["product_id"]),
            None,
        )
        qty_before = product_inv["total_quantity"] if product_inv else 0

        # Create and confirm outbound
        data = {"container_plan_id": seed_loaded_plan["plan_id"]}
        create_resp = await client.post("/api/v1/outbound-orders", json=data, headers=headers)
        order_id = create_resp.json()["data"]["id"]
        outbound_qty = sum(
            item["quantity"] for item in create_resp.json()["data"]["items"]
        )

        confirm_data = {
            "outbound_date": date.today().isoformat(),
            "operator": "Test Operator",
        }
        await client.post(
            f"/api/v1/outbound-orders/{order_id}/confirm",
            json=confirm_data,
            headers=headers,
        )

        # Check inventory after
        inv_resp2 = await client.get("/api/v1/warehouse/inventory", headers=headers)
        inv_after = inv_resp2.json()["data"]["items"]
        product_inv2 = next(
            (i for i in inv_after if i["product_id"] == seed_loaded_plan["product_id"]),
            None,
        )
        qty_after = product_inv2["total_quantity"] if product_inv2 else 0

        assert qty_after == qty_before - outbound_qty

    async def test_confirm_already_confirmed_fails(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        headers = get_auth_headers(admin_user)
        data = {"container_plan_id": seed_loaded_plan["plan_id"]}
        create_resp = await client.post("/api/v1/outbound-orders", json=data, headers=headers)
        order_id = create_resp.json()["data"]["id"]

        confirm_data = {
            "outbound_date": date.today().isoformat(),
            "operator": "Test Operator",
        }
        # First confirm
        await client.post(
            f"/api/v1/outbound-orders/{order_id}/confirm",
            json=confirm_data,
            headers=headers,
        )

        # Second confirm should fail
        resp = await client.post(
            f"/api/v1/outbound-orders/{order_id}/confirm",
            json=confirm_data,
            headers=headers,
        )
        assert resp.status_code == 422


class TestCancelOutboundOrder:
    async def test_cancel_success(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        headers = get_auth_headers(admin_user)
        data = {"container_plan_id": seed_loaded_plan["plan_id"]}
        create_resp = await client.post("/api/v1/outbound-orders", json=data, headers=headers)
        order_id = create_resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/outbound-orders/{order_id}/cancel", headers=headers
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "cancelled"

    async def test_cancel_confirmed_fails(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        """Cannot cancel an already confirmed outbound order."""
        headers = get_auth_headers(admin_user)
        data = {"container_plan_id": seed_loaded_plan["plan_id"]}
        create_resp = await client.post("/api/v1/outbound-orders", json=data, headers=headers)
        order_id = create_resp.json()["data"]["id"]

        # Confirm first
        confirm_data = {
            "outbound_date": date.today().isoformat(),
            "operator": "Test Operator",
        }
        await client.post(
            f"/api/v1/outbound-orders/{order_id}/confirm",
            json=confirm_data,
            headers=headers,
        )

        # Try to cancel
        resp = await client.post(
            f"/api/v1/outbound-orders/{order_id}/cancel", headers=headers
        )
        assert resp.status_code == 422
