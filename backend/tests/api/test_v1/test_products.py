from httpx import AsyncClient

from app.models.user import User
from tests.conftest import get_auth_headers
from tests.factories import make_product_data


class TestCreateProduct:
    async def test_create_product(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        data = make_product_data()
        resp = await client.post("/api/v1/products", json=data, headers=headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["sku_code"] == data["sku_code"]
        assert body["data"]["name_cn"] == "测试零食"
        assert body["data"]["status"] == "active"

    async def test_create_duplicate_sku(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        data = make_product_data(sku_code="DUP-SKU-001")
        await client.post("/api/v1/products", json=data, headers=headers)
        resp = await client.post("/api/v1/products", json=data, headers=headers)
        assert resp.status_code == 409

    async def test_create_product_no_auth(self, client: AsyncClient):
        data = make_product_data()
        resp = await client.post("/api/v1/products", json=data)
        assert resp.status_code == 401

    async def test_create_product_viewer_forbidden(self, client: AsyncClient, viewer_user: User):
        headers = get_auth_headers(viewer_user)
        data = make_product_data()
        resp = await client.post("/api/v1/products", json=data, headers=headers)
        assert resp.status_code == 403


class TestListProducts:
    async def test_list_products(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        # Create a product first
        data = make_product_data()
        await client.post("/api/v1/products", json=data, headers=headers)

        resp = await client.get("/api/v1/products", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["total"] >= 1
        assert len(body["data"]["items"]) >= 1

    async def test_list_products_with_keyword(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/products?keyword=nonexistent_xxx", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 0


class TestGetProduct:
    async def test_get_product(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        data = make_product_data()
        create_resp = await client.post("/api/v1/products", json=data, headers=headers)
        product_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/products/{product_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == product_id

    async def test_get_product_not_found(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        import uuid

        resp = await client.get(f"/api/v1/products/{uuid.uuid4()}", headers=headers)
        assert resp.status_code == 404


class TestUpdateProduct:
    async def test_update_product(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        data = make_product_data()
        create_resp = await client.post("/api/v1/products", json=data, headers=headers)
        product_id = create_resp.json()["data"]["id"]

        resp = await client.put(
            f"/api/v1/products/{product_id}",
            json={"name_cn": "更新后的名称"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["name_cn"] == "更新后的名称"


class TestUpdateProductStatus:
    async def test_deactivate_product(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        data = make_product_data()
        create_resp = await client.post("/api/v1/products", json=data, headers=headers)
        product_id = create_resp.json()["data"]["id"]

        resp = await client.patch(
            f"/api/v1/products/{product_id}/status",
            json={"status": "inactive"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "inactive"
