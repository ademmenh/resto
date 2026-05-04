"""
E2E tests for all meals API endpoints.
Covers: create, get, list, update, delete, domain errors, RDTO shape.
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


# ── Create ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_meal_returns_201_with_rdto(client: AsyncClient, admin_headers):
    res = await client.post(
        "/api/v1/meals",
        json={"name": "E2E Burger", "price": "11.00", "category": "main"},
        headers=admin_headers,
    )
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["statusCode"] == 201
    assert data["message"] == "Meal created successfully"
    meal = data["data"]
    assert meal["name"] == "E2E Burger"
    assert meal["price"] == "11.00"
    assert meal["category"] == "main"
    assert meal["available"] is True
    assert "id" in meal
    assert "createdAt" in meal
    assert "updatedAt" in meal


@pytest.mark.asyncio
async def test_create_meal_with_description(client: AsyncClient, admin_headers):
    res = await client.post(
        "/api/v1/meals",
        json={"name": "Soup", "description": "Yummy soup", "price": "6.00", "category": "starter"},
        headers=admin_headers,
    )
    assert res.status_code == 201
    assert res.json()["data"]["description"] == "Yummy soup"


@pytest.mark.asyncio
async def test_create_meal_as_unavailable(client: AsyncClient, admin_headers):
    res = await client.post(
        "/api/v1/meals",
        json={"name": "Seasonal", "price": "9.00", "category": "special", "available": False},
        headers=admin_headers,
    )
    assert res.status_code == 201
    assert res.json()["data"]["available"] is False


@pytest.mark.asyncio
async def test_create_meal_requires_admin(client: AsyncClient, client_headers):
    res = await client.post(
        "/api/v1/meals",
        json={"name": "X", "price": "5.00", "category": "main"},
        headers=client_headers,
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_create_meal_unauthenticated(client: AsyncClient):
    res = await client.post("/api/v1/meals", json={"name": "X", "price": "5.00", "category": "main"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_create_meal_invalid_payload_returns_422(client: AsyncClient, admin_headers):
    res = await client.post("/api/v1/meals", json={"name": "X"}, headers=admin_headers)
    assert res.status_code == 422


# ── Get ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_meal_returns_rdto(client: AsyncClient, admin_headers):
    created = await client.post(
        "/api/v1/meals",
        json={"name": "Fetched Meal", "price": "8.00", "category": "main"},
        headers=admin_headers,
    )
    meal_id = created.json()["data"]["id"]
    res = await client.get(f"/api/v1/meals/{meal_id}", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["data"]["id"] == meal_id
    assert data["data"]["name"] == "Fetched Meal"


@pytest.mark.asyncio
async def test_get_meal_not_found_returns_404(client: AsyncClient, admin_headers):
    res = await client.get("/api/v1/meals/00000000-0000-0000-0000-000000000099", headers=admin_headers)
    assert res.status_code == 404
    assert res.json()["error"] == "NOT_FOUND"


# ── List ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_meals_returns_paginated_rdto(client: AsyncClient, admin_headers):
    await client.post("/api/v1/meals", json={"name": "ListMeal1", "price": "5.00", "category": "main"}, headers=admin_headers)
    res = await client.get("/api/v1/meals", headers=admin_headers)
    assert res.status_code == 200
    body = res.json()
    assert "data" in body
    assert "pagination" in body
    assert body["pagination"]["total"] >= 1


@pytest.mark.asyncio
async def test_list_meals_filter_by_category(client: AsyncClient, admin_headers):
    await client.post("/api/v1/meals", json={"name": "Starter X", "price": "4.00", "category": "starter"}, headers=admin_headers)
    res = await client.get("/api/v1/meals?category=starter", headers=admin_headers)
    assert res.status_code == 200
    meals = res.json()["data"]
    assert all(m["category"] == "starter" for m in meals)


@pytest.mark.asyncio
async def test_list_meals_filter_by_available(client: AsyncClient, admin_headers):
    await client.post("/api/v1/meals", json={"name": "Unavail Meal", "price": "5.00", "category": "main", "available": False}, headers=admin_headers)
    res = await client.get("/api/v1/meals?available=false", headers=admin_headers)
    assert res.status_code == 200
    meals = res.json()["data"]
    assert all(m["available"] is False for m in meals)


# ── Update ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_meal_returns_updated_rdto(client: AsyncClient, admin_headers):
    created = await client.post(
        "/api/v1/meals",
        json={"name": "Before", "price": "5.00", "category": "main"},
        headers=admin_headers,
    )
    meal_id = created.json()["data"]["id"]
    res = await client.put(
        f"/api/v1/meals/{meal_id}",
        json={"name": "After", "price": "9.99"},
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "After"
    assert res.json()["data"]["price"] == "9.99"


@pytest.mark.asyncio
async def test_update_meal_not_found_returns_404(client: AsyncClient, admin_headers):
    res = await client.put(
        "/api/v1/meals/00000000-0000-0000-0000-000000000099",
        json={"name": "X"},
        headers=admin_headers,
    )
    assert res.status_code == 404
    assert res.json()["error"] == "NOT_FOUND"


# ── Delete ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_meal_returns_204(client: AsyncClient, admin_headers):
    created = await client.post(
        "/api/v1/meals",
        json={"name": "ToDelete", "price": "5.00", "category": "main"},
        headers=admin_headers,
    )
    meal_id = created.json()["data"]["id"]
    res = await client.delete(f"/api/v1/meals/{meal_id}", headers=admin_headers)
    assert res.status_code == 204


@pytest.mark.asyncio
async def test_delete_meal_not_found_returns_404(client: AsyncClient, admin_headers):
    res = await client.delete("/api/v1/meals/00000000-0000-0000-0000-000000000099", headers=admin_headers)
    assert res.status_code == 404
    assert res.json()["error"] == "NOT_FOUND"
