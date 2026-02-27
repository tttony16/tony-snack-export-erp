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
async def seed_goods_ready_so(client: AsyncClient, admin_user: User) -> dict:
    """Create a SO in goods_ready status (full chain: SO→PO→receiving→goods_ready)."""
    headers = get_auth_headers(admin_user)

    # Create customer, product, supplier
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

    # Receive all goods → triggers R11 → SO becomes goods_ready
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

    return {"so_id": so_id, "product_id": product_id, "customer_id": customer_id}


class TestCreateContainerPlan:
    async def test_create_success(
        self, client: AsyncClient, admin_user: User, seed_goods_ready_so: dict
    ):
        headers = get_auth_headers(admin_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        resp = await client.post("/api/v1/containers", json=data, headers=headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["plan_no"].startswith("CL-")
        assert body["data"]["status"] == "planning"

    async def test_create_r04_not_goods_ready(self, client: AsyncClient, admin_user: User):
        """R04: only goods_ready SOs can be used for container plan."""
        headers = get_auth_headers(admin_user)
        # Create a SO in draft status
        cust_resp = await client.post(
            "/api/v1/customers", json=make_customer_data(), headers=headers
        )
        prod_resp = await client.post("/api/v1/products", json=make_product_data(), headers=headers)
        so_data = make_sales_order_data(
            cust_resp.json()["data"]["id"], prod_resp.json()["data"]["id"]
        )
        so_resp = await client.post("/api/v1/sales-orders", json=so_data, headers=headers)
        so_id = so_resp.json()["data"]["id"]

        data = make_container_plan_data([so_id])
        resp = await client.post("/api/v1/containers", json=data, headers=headers)
        assert resp.status_code == 422

    async def test_create_no_auth(self, client: AsyncClient, seed_goods_ready_so: dict):
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        resp = await client.post("/api/v1/containers", json=data)
        assert resp.status_code in (401, 403)

    async def test_create_viewer_forbidden(
        self, client: AsyncClient, viewer_user: User, seed_goods_ready_so: dict
    ):
        headers = get_auth_headers(viewer_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        resp = await client.post("/api/v1/containers", json=data, headers=headers)
        assert resp.status_code == 403


class TestListContainerPlans:
    async def test_list(self, client: AsyncClient, admin_user: User, seed_goods_ready_so: dict):
        headers = get_auth_headers(admin_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        await client.post("/api/v1/containers", json=data, headers=headers)

        resp = await client.get("/api/v1/containers", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 1


class TestGetContainerPlan:
    async def test_get(self, client: AsyncClient, admin_user: User, seed_goods_ready_so: dict):
        headers = get_auth_headers(admin_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        create_resp = await client.post("/api/v1/containers", json=data, headers=headers)
        plan_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/containers/{plan_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == plan_id

    async def test_get_not_found(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(f"/api/v1/containers/{uuid.uuid4()}", headers=headers)
        assert resp.status_code == 404


class TestContainerItems:
    async def test_add_item(self, client: AsyncClient, admin_user: User, seed_goods_ready_so: dict):
        headers = get_auth_headers(admin_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        create_resp = await client.post("/api/v1/containers", json=data, headers=headers)
        plan_id = create_resp.json()["data"]["id"]

        item_data = {
            "container_seq": 1,
            "product_id": seed_goods_ready_so["product_id"],
            "sales_order_id": seed_goods_ready_so["so_id"],
            "quantity": 50,
            "volume_cbm": "1.5",
            "weight_kg": "500.0",
        }
        resp = await client.post(
            f"/api/v1/containers/{plan_id}/items", json=item_data, headers=headers
        )
        assert resp.status_code == 201

    async def test_delete_item(
        self, client: AsyncClient, admin_user: User, seed_goods_ready_so: dict
    ):
        headers = get_auth_headers(admin_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        create_resp = await client.post("/api/v1/containers", json=data, headers=headers)
        plan_id = create_resp.json()["data"]["id"]

        item_data = {
            "container_seq": 1,
            "product_id": seed_goods_ready_so["product_id"],
            "sales_order_id": seed_goods_ready_so["so_id"],
            "quantity": 50,
            "volume_cbm": "1.5",
            "weight_kg": "500.0",
        }
        item_resp = await client.post(
            f"/api/v1/containers/{plan_id}/items", json=item_data, headers=headers
        )
        item_id = item_resp.json()["data"]["id"]

        resp = await client.delete(f"/api/v1/containers/{plan_id}/items/{item_id}", headers=headers)
        assert resp.status_code == 204


class TestContainerSummaryAndValidation:
    async def test_summary(self, client: AsyncClient, admin_user: User, seed_goods_ready_so: dict):
        headers = get_auth_headers(admin_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        create_resp = await client.post("/api/v1/containers", json=data, headers=headers)
        plan_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/containers/{plan_id}/summary", headers=headers)
        assert resp.status_code == 200
        assert "items" in resp.json()["data"]

    async def test_validate(self, client: AsyncClient, admin_user: User, seed_goods_ready_so: dict):
        headers = get_auth_headers(admin_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        create_resp = await client.post("/api/v1/containers", json=data, headers=headers)
        plan_id = create_resp.json()["data"]["id"]

        resp = await client.post(f"/api/v1/containers/{plan_id}/validate", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["is_valid"] is True  # empty plan is valid


class TestConfirmContainerPlan:
    async def test_confirm_r12(
        self, client: AsyncClient, admin_user: User, seed_goods_ready_so: dict
    ):
        """R12: Confirm plan → SO status becomes container_planned."""
        headers = get_auth_headers(admin_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        create_resp = await client.post("/api/v1/containers", json=data, headers=headers)
        plan_id = create_resp.json()["data"]["id"]

        resp = await client.post(f"/api/v1/containers/{plan_id}/confirm", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "confirmed"

        # Check SO status
        so_resp = await client.get(
            f"/api/v1/sales-orders/{seed_goods_ready_so['so_id']}", headers=headers
        )
        assert so_resp.json()["data"]["status"] == "container_planned"

    async def test_confirm_non_planning_fails(
        self, client: AsyncClient, admin_user: User, seed_goods_ready_so: dict
    ):
        headers = get_auth_headers(admin_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        create_resp = await client.post("/api/v1/containers", json=data, headers=headers)
        plan_id = create_resp.json()["data"]["id"]
        await client.post(f"/api/v1/containers/{plan_id}/confirm", headers=headers)

        # Try again
        resp = await client.post(f"/api/v1/containers/{plan_id}/confirm", headers=headers)
        assert resp.status_code == 422


class TestStuffing:
    async def test_stuffing_r13(
        self, client: AsyncClient, admin_user: User, seed_goods_ready_so: dict
    ):
        """R13: All containers stuffed → SO becomes container_loaded."""
        headers = get_auth_headers(admin_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        create_resp = await client.post("/api/v1/containers", json=data, headers=headers)
        plan_id = create_resp.json()["data"]["id"]

        # Confirm plan first
        await client.post(f"/api/v1/containers/{plan_id}/confirm", headers=headers)

        # Record stuffing for the single container
        stuffing_data = {
            "container_seq": 1,
            "container_no": "CSLU1234567",
            "seal_no": "SL123456",
            "stuffing_date": date.today().isoformat(),
            "stuffing_location": "Shanghai Warehouse",
        }
        resp = await client.post(
            f"/api/v1/containers/{plan_id}/stuffing", json=stuffing_data, headers=headers
        )
        assert resp.status_code == 201

        # Check plan status is loaded
        plan_resp = await client.get(f"/api/v1/containers/{plan_id}", headers=headers)
        assert plan_resp.json()["data"]["status"] == "loaded"

        # Check SO status is container_loaded
        so_resp = await client.get(
            f"/api/v1/sales-orders/{seed_goods_ready_so['so_id']}", headers=headers
        )
        assert so_resp.json()["data"]["status"] == "container_loaded"

    async def test_stuffing_duplicate_seq_fails(
        self, client: AsyncClient, admin_user: User, seed_goods_ready_so: dict
    ):
        headers = get_auth_headers(admin_user)
        data = make_container_plan_data([seed_goods_ready_so["so_id"]])
        create_resp = await client.post("/api/v1/containers", json=data, headers=headers)
        plan_id = create_resp.json()["data"]["id"]
        await client.post(f"/api/v1/containers/{plan_id}/confirm", headers=headers)

        stuffing_data = {
            "container_seq": 1,
            "container_no": "CSLU1234567",
            "seal_no": "SL123456",
            "stuffing_date": date.today().isoformat(),
        }
        await client.post(
            f"/api/v1/containers/{plan_id}/stuffing", json=stuffing_data, headers=headers
        )

        # Try same seq again
        resp = await client.post(
            f"/api/v1/containers/{plan_id}/stuffing", json=stuffing_data, headers=headers
        )
        assert resp.status_code == 422
