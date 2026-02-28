import uuid
from datetime import date

import pytest
from httpx import AsyncClient

from app.models.enums import InspectionResult, UnitType
from app.models.user import User
from tests.conftest import get_auth_headers
from tests.factories import (
    make_customer_data,
    make_product_data,
    make_purchase_order_data,
    make_receiving_note_data,
    make_sales_order_data,
)


@pytest.fixture
async def seed_customer(client: AsyncClient, admin_user: User) -> str:
    headers = get_auth_headers(admin_user)
    resp = await client.post("/api/v1/customers", json=make_customer_data(), headers=headers)
    return resp.json()["data"]["id"]


@pytest.fixture
async def seed_product(client: AsyncClient, admin_user: User) -> str:
    headers = get_auth_headers(admin_user)
    resp = await client.post("/api/v1/products", json=make_product_data(), headers=headers)
    return resp.json()["data"]["id"]


@pytest.fixture
async def seed_supplier(client: AsyncClient, admin_user: User) -> str:
    from tests.factories import make_supplier_data

    headers = get_auth_headers(admin_user)
    resp = await client.post("/api/v1/suppliers", json=make_supplier_data(), headers=headers)
    return resp.json()["data"]["id"]


@pytest.fixture
async def seed_confirmed_po(
    client: AsyncClient,
    admin_user: User,
    seed_supplier: str,
    seed_product: str,
    seed_customer: str,
) -> dict:
    """Create a confirmed PO linked to a SO, return PO data with item IDs."""
    headers = get_auth_headers(admin_user)

    # Create SO and confirm it
    so_data = make_sales_order_data(seed_customer, seed_product)
    so_resp = await client.post("/api/v1/sales-orders", json=so_data, headers=headers)
    so_id = so_resp.json()["data"]["id"]
    so_item_id = so_resp.json()["data"]["items"][0]["id"]

    await client.post(f"/api/v1/sales-orders/{so_id}/confirm", headers=headers)

    # Create PO linked to SO
    po_data = make_purchase_order_data(
        seed_supplier,
        seed_product,
        sales_order_ids=[so_id],
        items=[
            {
                "product_id": seed_product,
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

    # Confirm PO
    await client.post(f"/api/v1/purchase-orders/{po_id}/confirm", headers=headers)

    return {
        "po_id": po_id,
        "po_item_id": po_item_id,
        "so_id": so_id,
        "so_item_id": so_item_id,
        "product_id": seed_product,
    }


class TestCreateReceivingNote:
    async def test_create_success(
        self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict
    ):
        headers = get_auth_headers(admin_user)
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
            items=[
                {
                    "purchase_order_item_id": seed_confirmed_po["po_item_id"],
                    "product_id": seed_confirmed_po["product_id"],
                    "expected_quantity": 100,
                    "actual_quantity": 100,
                    "inspection_result": InspectionResult.PASSED.value,
                    "failed_quantity": 0,
                    "production_date": date.today().isoformat(),
                }
            ],
        )
        resp = await client.post("/api/v1/warehouse/receiving-notes", json=data, headers=headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["note_no"].startswith("RCV-")
        assert len(body["data"]["items"]) == 1

    async def test_create_r03_exceeds_remaining(
        self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict
    ):
        """R03: actual_quantity cannot exceed PO item remaining."""
        headers = get_auth_headers(admin_user)
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
            items=[
                {
                    "purchase_order_item_id": seed_confirmed_po["po_item_id"],
                    "product_id": seed_confirmed_po["product_id"],
                    "expected_quantity": 100,
                    "actual_quantity": 999,  # exceeds PO quantity of 100
                    "inspection_result": InspectionResult.PASSED.value,
                    "failed_quantity": 0,
                    "production_date": date.today().isoformat(),
                }
            ],
        )
        resp = await client.post("/api/v1/warehouse/receiving-notes", json=data, headers=headers)
        assert resp.status_code == 422

    async def test_create_no_auth(self, client: AsyncClient, seed_confirmed_po: dict):
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
        )
        resp = await client.post("/api/v1/warehouse/receiving-notes", json=data)
        assert resp.status_code in (401, 403)

    async def test_create_viewer_forbidden(
        self, client: AsyncClient, viewer_user: User, seed_confirmed_po: dict
    ):
        headers = get_auth_headers(viewer_user)
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
        )
        resp = await client.post("/api/v1/warehouse/receiving-notes", json=data, headers=headers)
        assert resp.status_code == 403


class TestListReceivingNotes:
    async def test_list(self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict):
        headers = get_auth_headers(admin_user)
        # Create a receiving note first
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
        )
        await client.post("/api/v1/warehouse/receiving-notes", json=data, headers=headers)

        resp = await client.get("/api/v1/warehouse/receiving-notes", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 1


class TestGetReceivingNote:
    async def test_get_with_items(
        self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict
    ):
        headers = get_auth_headers(admin_user)
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
        )
        create_resp = await client.post(
            "/api/v1/warehouse/receiving-notes", json=data, headers=headers
        )
        note_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/warehouse/receiving-notes/{note_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == note_id

    async def test_get_not_found(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(
            f"/api/v1/warehouse/receiving-notes/{uuid.uuid4()}", headers=headers
        )
        assert resp.status_code == 404


class TestR11AutoStatusUpdate:
    async def test_r11_so_goods_ready(
        self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict
    ):
        """R11: When all goods received, SO status should auto-update to goods_ready."""
        headers = get_auth_headers(admin_user)

        # Receive all goods (quantity=100, matching the SO quantity)
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
            items=[
                {
                    "purchase_order_item_id": seed_confirmed_po["po_item_id"],
                    "product_id": seed_confirmed_po["product_id"],
                    "expected_quantity": 100,
                    "actual_quantity": 100,
                    "inspection_result": InspectionResult.PASSED.value,
                    "failed_quantity": 0,
                    "production_date": date.today().isoformat(),
                }
            ],
        )
        await client.post("/api/v1/warehouse/receiving-notes", json=data, headers=headers)

        # Check SO status is now goods_ready
        so_resp = await client.get(
            f"/api/v1/sales-orders/{seed_confirmed_po['so_id']}", headers=headers
        )
        assert so_resp.json()["data"]["status"] == "goods_ready"


class TestInventory:
    async def test_inventory_by_product(
        self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict
    ):
        headers = get_auth_headers(admin_user)
        # Create receiving note first
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
        )
        await client.post("/api/v1/warehouse/receiving-notes", json=data, headers=headers)

        resp = await client.get("/api/v1/warehouse/inventory", headers=headers)
        assert resp.status_code == 200

    async def test_readiness_check(
        self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict
    ):
        headers = get_auth_headers(admin_user)
        resp = await client.get(
            f"/api/v1/warehouse/inventory/readiness/{seed_confirmed_po['so_id']}",
            headers=headers,
        )
        assert resp.status_code == 200
        assert "is_ready" in resp.json()["data"]


class TestInventoryBatches:
    async def test_batch_list(
        self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict
    ):
        """Batch listing endpoint returns inventory records."""
        headers = get_auth_headers(admin_user)
        # Create inventory via receiving
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
        )
        await client.post("/api/v1/warehouse/receiving-notes", json=data, headers=headers)

        resp = await client.get("/api/v1/warehouse/inventory/batches", headers=headers)
        assert resp.status_code == 200
        batches = resp.json()["data"]
        assert len(batches) > 0
        # Verify batch fields
        batch = batches[0]
        assert "id" in batch
        assert "product_id" in batch
        assert "batch_no" in batch
        assert "production_date" in batch
        assert "available_quantity" in batch
        assert "reserved_quantity" in batch

    async def test_batch_list_filter_by_product(
        self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict
    ):
        headers = get_auth_headers(admin_user)
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
        )
        await client.post("/api/v1/warehouse/receiving-notes", json=data, headers=headers)

        resp = await client.get(
            f"/api/v1/warehouse/inventory/batches?product_id={seed_confirmed_po['product_id']}",
            headers=headers,
        )
        assert resp.status_code == 200
        batches = resp.json()["data"]
        assert all(b["product_id"] == seed_confirmed_po["product_id"] for b in batches)

    async def test_inventory_by_product_has_reserved(
        self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict
    ):
        """Inventory by product should include reserved_quantity."""
        headers = get_auth_headers(admin_user)
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
        )
        await client.post("/api/v1/warehouse/receiving-notes", json=data, headers=headers)

        resp = await client.get("/api/v1/warehouse/inventory", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert len(items) > 0
        # Check reserved_quantity field exists
        assert "reserved_quantity" in items[0]


class TestPendingInspection:
    async def test_pending_inspection_empty(
        self, client: AsyncClient, admin_user: User
    ):
        """Pending inspection list returns successfully even with no data."""
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/warehouse/inventory/pending-inspection", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 0

    async def test_pending_inspection_with_partial_passed(
        self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict
    ):
        """Items with partial_passed inspection should appear in pending list."""
        headers = get_auth_headers(admin_user)
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
            items=[
                {
                    "purchase_order_item_id": seed_confirmed_po["po_item_id"],
                    "product_id": seed_confirmed_po["product_id"],
                    "expected_quantity": 100,
                    "actual_quantity": 80,
                    "inspection_result": InspectionResult.PARTIAL_PASSED.value,
                    "failed_quantity": 20,
                    "failure_reason": "包装破损",
                    "production_date": date.today().isoformat(),
                }
            ],
        )
        await client.post("/api/v1/warehouse/receiving-notes", json=data, headers=headers)

        resp = await client.get("/api/v1/warehouse/inventory/pending-inspection", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 1
        items = resp.json()["data"]["items"]
        assert any(i["inspection_result"] == "partial_passed" for i in items)

    async def test_pending_inspection_excludes_passed(
        self, client: AsyncClient, admin_user: User, seed_confirmed_po: dict
    ):
        """Items with passed inspection should NOT appear in pending list."""
        headers = get_auth_headers(admin_user)
        data = make_receiving_note_data(
            seed_confirmed_po["po_id"],
            seed_confirmed_po["po_item_id"],
            seed_confirmed_po["product_id"],
        )
        await client.post("/api/v1/warehouse/receiving-notes", json=data, headers=headers)

        resp = await client.get("/api/v1/warehouse/inventory/pending-inspection", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        # None should be "passed"
        assert all(i["inspection_result"] != "passed" for i in items)

    async def test_pending_inspection_viewer_allowed(
        self, client: AsyncClient, viewer_user: User
    ):
        """Viewer should have access to pending inspection (INVENTORY_VIEW permission)."""
        headers = get_auth_headers(viewer_user)
        resp = await client.get("/api/v1/warehouse/inventory/pending-inspection", headers=headers)
        assert resp.status_code == 200
