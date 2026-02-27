from httpx import AsyncClient

from app.models.user import User
from tests.conftest import get_auth_headers


class TestLogin:
    async def test_login_success(self, client: AsyncClient, admin_user: User):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": admin_user.username, "password": "testpass123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    async def test_login_wrong_password(self, client: AsyncClient, admin_user: User):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": admin_user.username, "password": "wrongpass"},
        )
        assert resp.status_code == 400
        assert resp.json()["code"] == 40101

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "nobody", "password": "whatever"},
        )
        assert resp.status_code == 400


class TestMe:
    async def test_get_me(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.get("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["username"] == admin_user.username
        assert data["role"] == "super_admin"

    async def test_get_me_no_token(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401


class TestRefresh:
    async def test_refresh_token(self, client: AsyncClient, admin_user: User):
        # Login first
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": admin_user.username, "password": "testpass123"},
        )
        refresh_token = login_resp.json()["data"]["refresh_token"]

        # Refresh
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()["data"]

    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        assert resp.status_code == 400


class TestLogout:
    async def test_logout(self, client: AsyncClient, admin_user: User):
        headers = get_auth_headers(admin_user)
        resp = await client.post("/api/v1/auth/logout", headers=headers)
        assert resp.status_code == 200
