"""
E2E tests for the users API endpoints.
Admin-only routes: list, get, update, delete.
"""
import pytest
from httpx import AsyncClient
from src.auth.domain.ports import TokenPayload
from src.auth.infrastructure.jwt_adapter import JwtAdapter


@pytest.fixture
def admin_headers(config) -> dict[str, str]:
    token = JwtAdapter(config).sign(
        TokenPayload(sub="00000000-0000-0000-0000-000000000001", email="admin@test.local", role="admin")
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_headers(config) -> dict[str, str]:
    token = JwtAdapter(config).sign(
        TokenPayload(sub="00000000-0000-0000-0000-000000000002", email="client@test.local", role="client")
    )
    return {"Authorization": f"Bearer {token}"}


async def _register(client: AsyncClient, email: str, name: str = "User") -> dict:
    res = await client.post("/api/v1/auth/register", json={
        "name": name,
        "email": email,
        "password": "password123",
    })
    assert res.status_code == 201, res.text
    # Clear cookies so they don't override Authorization header in subsequent calls
    client.cookies.clear()
    return res.json()["data"]


# ── List ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_users_returns_paginated_rdto(client: AsyncClient, admin_headers):
    await _register(client, "listuser@users.e2e")
    res = await client.get("/api/v1/users", headers=admin_headers)
    assert res.status_code == 200
    body = res.json()
    assert "data" in body
    assert "pagination" in body
    assert body["pagination"]["total"] >= 1
    user = body["data"][0]
    assert "id" in user
    assert "name" in user
    assert "email" in user
    assert "role" in user
    assert "createdAt" in user


@pytest.mark.asyncio
async def test_list_users_requires_admin(client: AsyncClient, client_headers):
    res = await client.get("/api/v1/users", headers=client_headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_list_users_unauthenticated_returns_401(client: AsyncClient):
    res = await client.get("/api/v1/users")
    assert res.status_code == 401


# ── Get ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_user_returns_rdto(client: AsyncClient, admin_headers):
    user = await _register(client, "getuser@users.e2e", "GetUser")
    user_id = user["id"]
    res = await client.get(f"/api/v1/users/{user_id}", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["id"] == user_id
    assert data["name"] == "GetUser"
    assert data["email"] == "getuser@users.e2e"


@pytest.mark.asyncio
async def test_get_user_not_found_returns_404(client: AsyncClient, admin_headers):
    res = await client.get("/api/v1/users/00000000-0000-0000-0000-000000000099", headers=admin_headers)
    assert res.status_code == 404
    assert res.json()["error"] == "NOT_FOUND"


# ── Update ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_user_name(client: AsyncClient, admin_headers):
    user = await _register(client, "updateuser@users.e2e", "OldName")
    user_id = user["id"]
    res = await client.put(f"/api/v1/users/{user_id}", json={"name": "NewName"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "NewName"


@pytest.mark.asyncio
async def test_update_user_not_found_returns_404(client: AsyncClient, admin_headers):
    res = await client.put(
        "/api/v1/users/00000000-0000-0000-0000-000000000099",
        json={"name": "X"},
        headers=admin_headers,
    )
    assert res.status_code == 404
    assert res.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_update_user_duplicate_email_returns_409(client: AsyncClient, admin_headers):
    u1 = await _register(client, "u1.dup@users.e2e", "U1")
    u2 = await _register(client, "u2.dup@users.e2e", "U2")
    res = await client.put(
        f"/api/v1/users/{u1['id']}",
        json={"email": "u2.dup@users.e2e"},
        headers=admin_headers,
    )
    assert res.status_code == 409
    assert res.json()["error"] == "CONFLICT"


# ── Delete ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_user_returns_204(client: AsyncClient, admin_headers):
    user = await _register(client, "deluser@users.e2e", "DelUser")
    res = await client.delete(f"/api/v1/users/{user['id']}", headers=admin_headers)
    assert res.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_not_found_returns_404(client: AsyncClient, admin_headers):
    res = await client.delete("/api/v1/users/00000000-0000-0000-0000-000000000099", headers=admin_headers)
    assert res.status_code == 404
    assert res.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_user_requires_admin(client: AsyncClient, client_headers):
    res = await client.delete("/api/v1/users/00000000-0000-0000-0000-000000000001", headers=client_headers)
    assert res.status_code == 403
