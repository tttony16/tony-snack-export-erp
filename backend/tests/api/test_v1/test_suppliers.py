import uuid

from httpx import AsyncClient

from app.models.user import User
from tests.conftest import get_auth_headers
from tests.factories import make_product_data, make_supplier_data


class TestCreateSupplier:
    async def test_create_supplier(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        data = make_supplier_data()
        resp = await client.post("/api/v1/suppliers", json=data, headers=headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["supplier_code"].startswith("SUP-")
        assert body["data"]["name"] == data["name"]

    async def test_create_supplier_viewer_forbidden(self, client: AsyncClient, viewer_user: User):
        headers = get_auth_headers(viewer_user)
        data = make_supplier_data()
        resp = await client.post("/api/v1/suppliers", json=data, headers=headers)
        assert resp.status_code == 403


class TestListSuppliers:
    async def test_list_suppliers(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        await client.post("/api/v1/suppliers", json=make_supplier_data(), headers=headers)
        resp = await client.get("/api/v1/suppliers", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 1


class TestGetSupplier:
    async def test_get_supplier(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/suppliers", json=make_supplier_data(), headers=headers
        )
        supplier_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/suppliers/{supplier_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == supplier_id

    async def test_get_supplier_not_found(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(f"/api/v1/suppliers/{uuid.uuid4()}", headers=headers)
        assert resp.status_code == 404


class TestUpdateSupplier:
    async def test_update_supplier(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/suppliers", json=make_supplier_data(), headers=headers
        )
        supplier_id = create_resp.json()["data"]["id"]

        resp = await client.put(
            f"/api/v1/suppliers/{supplier_id}",
            json={"name": "Updated Supplier"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Updated Supplier"


class TestSupplierProducts:
    async def test_add_and_remove_product(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)

        # Create supplier
        sup_resp = await client.post(
            "/api/v1/suppliers", json=make_supplier_data(), headers=headers
        )
        supplier_id = sup_resp.json()["data"]["id"]

        # Create product
        prod_resp = await client.post("/api/v1/products", json=make_product_data(), headers=headers)
        product_id = prod_resp.json()["data"]["id"]

        # Add product to supplier
        resp = await client.post(
            f"/api/v1/suppliers/{supplier_id}/products",
            json={"product_id": product_id, "supply_price": "12.50"},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["product_id"] == product_id

        # Adding same product again should conflict
        resp2 = await client.post(
            f"/api/v1/suppliers/{supplier_id}/products",
            json={"product_id": product_id},
            headers=headers,
        )
        assert resp2.status_code == 409

        # Remove product
        resp3 = await client.delete(
            f"/api/v1/suppliers/{supplier_id}/products/{product_id}",
            headers=headers,
        )
        assert resp3.status_code == 204
