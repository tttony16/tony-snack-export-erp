import uuid

from httpx import AsyncClient

from app.models.user import User
from tests.conftest import get_auth_headers
from tests.factories import make_customer_data


class TestCreateCustomer:
    async def test_create_customer(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        data = make_customer_data()
        resp = await client.post("/api/v1/customers", json=data, headers=headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["customer_code"].startswith("CUS-")
        assert body["data"]["name"] == data["name"]
        assert body["data"]["currency"] == "USD"

    async def test_create_customer_viewer_forbidden(self, client: AsyncClient, viewer_user: User):
        headers = get_auth_headers(viewer_user)
        data = make_customer_data()
        resp = await client.post("/api/v1/customers", json=data, headers=headers)
        assert resp.status_code == 403


class TestListCustomers:
    async def test_list_customers(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        await client.post("/api/v1/customers", json=make_customer_data(), headers=headers)
        resp = await client.get("/api/v1/customers", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 1

    async def test_list_customers_filter_country(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        await client.post(
            "/api/v1/customers",
            json=make_customer_data(country="Japan"),
            headers=headers,
        )
        resp = await client.get("/api/v1/customers?country=Japan", headers=headers)
        assert resp.status_code == 200
        for item in resp.json()["data"]["items"]:
            assert item["country"] == "Japan"


class TestGetCustomer:
    async def test_get_customer(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/customers", json=make_customer_data(), headers=headers
        )
        customer_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/customers/{customer_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == customer_id

    async def test_get_customer_not_found(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get(f"/api/v1/customers/{uuid.uuid4()}", headers=headers)
        assert resp.status_code == 404


class TestUpdateCustomer:
    async def test_update_customer(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        create_resp = await client.post(
            "/api/v1/customers", json=make_customer_data(), headers=headers
        )
        customer_id = create_resp.json()["data"]["id"]

        resp = await client.put(
            f"/api/v1/customers/{customer_id}",
            json={"name": "Updated Name", "contact_person": "New Contact"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Updated Name"
