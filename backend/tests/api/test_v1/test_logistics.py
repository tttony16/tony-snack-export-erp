import uuid
from datetime import date

import pytest
from httpx import AsyncClient

from app.models.enums import (
    CurrencyType,
    InspectionResult,
    LogisticsCostType,
    UnitType,
)
from app.models.user import User
from tests.conftest import get_auth_headers
from tests.factories import (
    make_container_plan_data,
    make_customer_data,
    make_logistics_record_data,
    make_product_data,
    make_purchase_order_data,
    make_receiving_note_data,
    make_sales_order_data,
    make_supplier_data,
)


@pytest.fixture
async def seed_loaded_plan(client: AsyncClient, admin_user: User) -> dict:
    """Create a loaded container plan (full chain: SO→PO→RCV→goods_ready→plan→confirm→stuffing→loaded)."""
    headers = get_auth_headers(admin_user)

    # Create entities
    cust_resp = await client.post("/api/v1/customers", json=make_customer_data(), headers=headers)
    customer_id = cust_resp.json()["data"]["id"]
    prod_resp = await client.post("/api/v1/products", json=make_product_data(), headers=headers)
    product_id = prod_resp.json()["data"]["id"]
    sup_resp = await client.post("/api/v1/suppliers", json=make_supplier_data(), headers=headers)
    supplier_id = sup_resp.json()["data"]["id"]

    # Create SO → confirm
    so_data = make_sales_order_data(customer_id, product_id)
    so_resp = await client.post("/api/v1/sales-orders", json=so_data, headers=headers)
    so_id = so_resp.json()["data"]["id"]
    so_item_id = so_resp.json()["data"]["items"][0]["id"]
    await client.post(f"/api/v1/sales-orders/{so_id}/confirm", headers=headers)

    # Create PO linked → confirm
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

    # Receive all goods → R11: goods_ready
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

    # Create container plan → confirm → stuff → loaded
    plan_data = make_container_plan_data([so_id])
    plan_resp = await client.post("/api/v1/containers", json=plan_data, headers=headers)
    plan_id = plan_resp.json()["data"]["id"]
    await client.post(f"/api/v1/containers/{plan_id}/confirm", headers=headers)

    stuffing_data = {
        "container_seq": 1,
        "container_no": "CSLU1234567",
        "seal_no": "SL123456",
        "stuffing_date": date.today().isoformat(),
    }
    await client.post(f"/api/v1/containers/{plan_id}/stuffing", json=stuffing_data, headers=headers)

    return {"plan_id": plan_id, "so_id": so_id}


class TestCreateLogisticsRecord:
    async def test_create_success(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        headers = get_auth_headers(admin_user)
        data = make_logistics_record_data(seed_loaded_plan["plan_id"])
        resp = await client.post("/api/v1/logistics", json=data, headers=headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["logistics_no"].startswith("LOG-")
        assert body["data"]["status"] == "booked"

    async def test_create_no_auth(self, client: AsyncClient, seed_loaded_plan: dict):
        data = make_logistics_record_data(seed_loaded_plan["plan_id"])
        resp = await client.post("/api/v1/logistics", json=data)
        assert resp.status_code in (401, 403)

    async def test_create_viewer_forbidden(
        self, client: AsyncClient, viewer_user: User, seed_loaded_plan: dict
    ):
        headers = get_auth_headers(viewer_user)
        data = make_logistics_record_data(seed_loaded_plan["plan_id"])
        resp = await client.post("/api/v1/logistics", json=data, headers=headers)
        assert resp.status_code == 403


class TestListLogisticsRecords:
    async def test_list(self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict):
        headers = get_auth_headers(admin_user)
        data = make_logistics_record_data(seed_loaded_plan["plan_id"])
        await client.post("/api/v1/logistics", json=data, headers=headers)

        resp = await client.get("/api/v1/logistics", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 1


class TestGetLogisticsRecord:
    async def test_get_with_costs(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        headers = get_auth_headers(admin_user)
        data = make_logistics_record_data(seed_loaded_plan["plan_id"])
        create_resp = await client.post("/api/v1/logistics", json=data, headers=headers)
        record_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/logistics/{record_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == record_id

    async def test_get_not_found(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(f"/api/v1/logistics/{uuid.uuid4()}", headers=headers)
        assert resp.status_code == 404


class TestLogisticsStatusUpdate:
    async def test_r14_shipped(self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict):
        """R14: loaded_on_ship → SO becomes shipped."""
        headers = get_auth_headers(admin_user)
        data = make_logistics_record_data(seed_loaded_plan["plan_id"])
        create_resp = await client.post("/api/v1/logistics", json=data, headers=headers)
        record_id = create_resp.json()["data"]["id"]

        # Progress through statuses
        await client.patch(
            f"/api/v1/logistics/{record_id}/status",
            json={"status": "customs_cleared"},
            headers=headers,
        )
        resp = await client.patch(
            f"/api/v1/logistics/{record_id}/status",
            json={"status": "loaded_on_ship"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "loaded_on_ship"

        # Check SO is shipped
        so_resp = await client.get(
            f"/api/v1/sales-orders/{seed_loaded_plan['so_id']}", headers=headers
        )
        assert so_resp.json()["data"]["status"] == "shipped"

    async def test_r15_delivered(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        """R15: delivered → SO becomes delivered."""
        headers = get_auth_headers(admin_user)
        data = make_logistics_record_data(seed_loaded_plan["plan_id"])
        create_resp = await client.post("/api/v1/logistics", json=data, headers=headers)
        record_id = create_resp.json()["data"]["id"]

        # Progress through all statuses
        for s in [
            "customs_cleared",
            "loaded_on_ship",
            "in_transit",
            "arrived",
            "picked_up",
            "delivered",
        ]:
            await client.patch(
                f"/api/v1/logistics/{record_id}/status",
                json={"status": s},
                headers=headers,
            )

        # Check SO is delivered
        so_resp = await client.get(
            f"/api/v1/sales-orders/{seed_loaded_plan['so_id']}", headers=headers
        )
        assert so_resp.json()["data"]["status"] == "delivered"

    async def test_status_backward_fails(
        self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict
    ):
        headers = get_auth_headers(admin_user)
        data = make_logistics_record_data(seed_loaded_plan["plan_id"])
        create_resp = await client.post("/api/v1/logistics", json=data, headers=headers)
        record_id = create_resp.json()["data"]["id"]

        await client.patch(
            f"/api/v1/logistics/{record_id}/status",
            json={"status": "customs_cleared"},
            headers=headers,
        )

        # Try to go backward
        resp = await client.patch(
            f"/api/v1/logistics/{record_id}/status",
            json={"status": "booked"},
            headers=headers,
        )
        assert resp.status_code == 422


class TestLogisticsCosts:
    async def test_add_cost(self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict):
        headers = get_auth_headers(admin_user)
        data = make_logistics_record_data(seed_loaded_plan["plan_id"])
        create_resp = await client.post("/api/v1/logistics", json=data, headers=headers)
        record_id = create_resp.json()["data"]["id"]

        cost_data = {
            "cost_type": LogisticsCostType.OCEAN_FREIGHT.value,
            "amount": "5000.00",
            "currency": CurrencyType.USD.value,
        }
        resp = await client.post(
            f"/api/v1/logistics/{record_id}/costs", json=cost_data, headers=headers
        )
        assert resp.status_code == 201

        # Check total_cost updated
        record_resp = await client.get(f"/api/v1/logistics/{record_id}", headers=headers)
        assert float(record_resp.json()["data"]["total_cost"]) == 5000.00

    async def test_delete_cost(self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict):
        headers = get_auth_headers(admin_user)
        data = make_logistics_record_data(seed_loaded_plan["plan_id"])
        create_resp = await client.post("/api/v1/logistics", json=data, headers=headers)
        record_id = create_resp.json()["data"]["id"]

        cost_data = {
            "cost_type": LogisticsCostType.OCEAN_FREIGHT.value,
            "amount": "5000.00",
            "currency": CurrencyType.USD.value,
        }
        cost_resp = await client.post(
            f"/api/v1/logistics/{record_id}/costs", json=cost_data, headers=headers
        )
        cost_id = cost_resp.json()["data"]["id"]

        resp = await client.delete(
            f"/api/v1/logistics/{record_id}/costs/{cost_id}", headers=headers
        )
        assert resp.status_code == 204


class TestLogisticsKanban:
    async def test_kanban(self, client: AsyncClient, admin_user: User, seed_loaded_plan: dict):
        headers = get_auth_headers(admin_user)
        data = make_logistics_record_data(seed_loaded_plan["plan_id"])
        await client.post("/api/v1/logistics", json=data, headers=headers)

        resp = await client.get("/api/v1/logistics/kanban", headers=headers)
        assert resp.status_code == 200
        assert "items" in resp.json()["data"]
