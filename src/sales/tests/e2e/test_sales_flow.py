"""
E2E tests for the sales API endpoints.
Covers: create, list, get, update (status), domain errors, RDTO shape.
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


async def _register_client(client: AsyncClient, email: str) -> tuple[str, str]:
    """Returns (user_id, access_token). Clears cookies to avoid contamination."""
    res = await client.post("/api/v1/auth/register", json={
        "name": "SaleClient",
        "email": email,
        "password": "pass",
    })
    assert res.status_code == 201, res.text
    user_id = res.json()["data"]["id"]
    access_token = res.json()["tokens"]["accessToken"]
    # Clear cookies so register cookies don't bleed into subsequent requests
    client.cookies.clear()
    return user_id, access_token


async def _create_meal(client: AsyncClient, admin_headers: dict, name: str = "E2EMeal", available: bool = True) -> str:
    res = await client.post(
        "/api/v1/meals",
        json={"name": name, "price": "10.00", "category": "main", "available": available},
        headers=admin_headers,
    )
    assert res.status_code == 201, res.text
    return res.json()["data"]["id"]


# ── Create ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_sale_returns_201_with_rdto(client: AsyncClient, admin_headers):
    user_id, token = await _register_client(client, "sc1@sales.e2e")
    meal_id = await _create_meal(client, admin_headers)
    res = await client.post(
        "/api/v1/sales",
        json={"client_id": user_id, "meal_id": meal_id, "quantity": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["statusCode"] == 201
    sale = body["data"]
    assert sale["quantity"] == 2
    assert sale["status"] == "pending"
    assert sale["mealId"] == meal_id
    assert sale["clientId"] == user_id
    assert "unitPrice" in sale
    assert "totalPrice" in sale
    assert "createdAt" in sale


@pytest.mark.asyncio
async def test_create_sale_meal_not_found_returns_404(client: AsyncClient, admin_headers):
    user_id, token = await _register_client(client, "sc2@sales.e2e")
    res = await client.post(
        "/api/v1/sales",
        json={"client_id": user_id, "meal_id": "00000000-0000-0000-0000-000000000099", "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 404
    assert res.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_create_sale_meal_not_available_returns_422(client: AsyncClient, admin_headers):
    user_id, token = await _register_client(client, "sc3@sales.e2e")
    # Create meal as unavailable
    meal_id = await _create_meal(client, admin_headers, name="Unavail", available=False)
    res = await client.post(
        "/api/v1/sales",
        json={"client_id": user_id, "meal_id": meal_id, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_create_sale_unauthenticated_returns_401(client: AsyncClient, admin_headers):
    meal_id = await _create_meal(client, admin_headers)
    res = await client.post("/api/v1/sales", json={"client_id": "x", "meal_id": meal_id, "quantity": 1})
    assert res.status_code == 401


# ── Get ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_sale_as_owner(client: AsyncClient, admin_headers):
    user_id, token = await _register_client(client, "sc4@sales.e2e")
    meal_id = await _create_meal(client, admin_headers)
    created = await client.post(
        "/api/v1/sales",
        json={"client_id": user_id, "meal_id": meal_id, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    sale_id = created.json()["data"]["id"]
    res = await client.get(f"/api/v1/sales/{sale_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["data"]["id"] == sale_id


@pytest.mark.asyncio
async def test_get_sale_as_admin(client: AsyncClient, admin_headers):
    user_id, token = await _register_client(client, "sc5@sales.e2e")
    meal_id = await _create_meal(client, admin_headers)
    created = await client.post(
        "/api/v1/sales",
        json={"client_id": user_id, "meal_id": meal_id, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    sale_id = created.json()["data"]["id"]
    res = await client.get(f"/api/v1/sales/{sale_id}", headers=admin_headers)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_sale_not_found_returns_404(client: AsyncClient, admin_headers):
    res = await client.get("/api/v1/sales/00000000-0000-0000-0000-000000000099", headers=admin_headers)
    assert res.status_code == 404
    assert res.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_get_sale_access_denied_returns_403(client: AsyncClient, admin_headers):
    user_id, token = await _register_client(client, "sc6@sales.e2e")
    other_id, other_token = await _register_client(client, "sc7@sales.e2e")
    meal_id = await _create_meal(client, admin_headers)
    created = await client.post(
        "/api/v1/sales",
        json={"client_id": user_id, "meal_id": meal_id, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    sale_id = created.json()["data"]["id"]
    res = await client.get(f"/api/v1/sales/{sale_id}", headers={"Authorization": f"Bearer {other_token}"})
    assert res.status_code == 403


# ── List ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_sales_client_sees_own(client: AsyncClient, admin_headers):
    user_id, token = await _register_client(client, "sc8@sales.e2e")
    meal_id = await _create_meal(client, admin_headers)
    await client.post(
        "/api/v1/sales",
        json={"client_id": user_id, "meal_id": meal_id, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    res = await client.get("/api/v1/sales", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    sales = res.json()["data"]
    assert all(s["clientId"] == user_id for s in sales)


@pytest.mark.asyncio
async def test_list_sales_admin_sees_all(client: AsyncClient, admin_headers):
    res = await client.get("/api/v1/sales", headers=admin_headers)
    assert res.status_code == 200
    assert "pagination" in res.json()


# ── Update ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_sale_to_completed(client: AsyncClient, admin_headers):
    user_id, token = await _register_client(client, "sc9@sales.e2e")
    meal_id = await _create_meal(client, admin_headers)
    created = await client.post(
        "/api/v1/sales",
        json={"client_id": user_id, "meal_id": meal_id, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    sale_id = created.json()["data"]["id"]
    res = await client.put(f"/api/v1/sales/{sale_id}", json={"status": "completed"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "completed"


@pytest.mark.asyncio
async def test_update_sale_cancel_completed_returns_422(client: AsyncClient, admin_headers):
    user_id, token = await _register_client(client, "sc10@sales.e2e")
    meal_id = await _create_meal(client, admin_headers)
    created = await client.post(
        "/api/v1/sales",
        json={"client_id": user_id, "meal_id": meal_id, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    sale_id = created.json()["data"]["id"]
    await client.put(f"/api/v1/sales/{sale_id}", json={"status": "completed"}, headers=admin_headers)
    res = await client.put(f"/api/v1/sales/{sale_id}", json={"status": "cancelled"}, headers=admin_headers)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_update_sale_not_found_returns_404(client: AsyncClient, admin_headers):
    res = await client.put(
        "/api/v1/sales/00000000-0000-0000-0000-000000000099",
        json={"status": "completed"},
        headers=admin_headers,
    )
    assert res.status_code == 404
    assert res.json()["error"] == "NOT_FOUND"
