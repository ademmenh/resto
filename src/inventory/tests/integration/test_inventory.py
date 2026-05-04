"""
Integration tests for the inventory module.
All routes are admin-only; uses a synthetic admin JWT (no DB user needed).
"""

import pytest
from httpx import AsyncClient
from src.auth.domain.ports import TokenPayload
from src.auth.infrastructure.jwt_adapter import JwtAdapter


@pytest.fixture
def admin_headers(config) -> dict[str, str]:
    token = JwtAdapter(config).sign(
        TokenPayload(
            sub="00000000-0000-0000-0000-000000000001",
            email="admin@test.local",
            role="admin",
        )
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_item_returns_201(client: AsyncClient, admin_headers):
    response = await client.post(
        "/api/v1/inventory/items",
        json={"name": "Rice", "quantity": "50.0", "unit": "kg"},
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["data"]["name"] == "Rice"
    assert data["data"]["unit"] == "kg"
    assert "id" in data["data"]
    assert data["statusCode"] == 201


@pytest.mark.asyncio
async def test_get_item_returns_correct_data(client: AsyncClient, admin_headers):
    created = await client.post(
        "/api/v1/inventory/items",
        json={"name": "Salt", "quantity": "20.5", "unit": "kg"},
        headers=admin_headers,
    )
    item_id = created.json()["data"]["id"]

    response = await client.get(f"/api/v1/inventory/items/{item_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Salt"
    assert response.json()["data"]["unit"] == "kg"


@pytest.mark.asyncio
async def test_list_items_includes_created_item(client: AsyncClient, admin_headers):
    await client.post(
        "/api/v1/inventory/items",
        json={"name": "Olive Oil", "quantity": "10.0", "unit": "l"},
        headers=admin_headers,
    )
    response = await client.get("/api/v1/inventory/items", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    names = [i["name"] for i in body["data"]]
    assert "Olive Oil" in names
    assert "pagination" in body
    assert body["pagination"]["total"] >= 1


@pytest.mark.asyncio
async def test_update_item_name_and_unit(client: AsyncClient, admin_headers):
    created = await client.post(
        "/api/v1/inventory/items",
        json={"name": "Water", "quantity": "100.0", "unit": "l"},
        headers=admin_headers,
    )
    item_id = created.json()["data"]["id"]

    response = await client.put(
        f"/api/v1/inventory/items/{item_id}",
        json={"name": "Mineral Water", "unit": "l"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Mineral Water"


@pytest.mark.asyncio
async def test_add_quantity_increases_stock(client: AsyncClient, admin_headers):
    created = await client.post(
        "/api/v1/inventory/items",
        json={"name": "Sugar", "quantity": "5.0", "unit": "kg"},
        headers=admin_headers,
    )
    item_id = created.json()["data"]["id"]

    response = await client.post(
        f"/api/v1/inventory/items/{item_id}/add-quantity",
        json={"amount": "10.5"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    from decimal import Decimal

    assert Decimal(response.json()["data"]["quantity"]) == Decimal("15.5")


@pytest.mark.asyncio
async def test_reduce_quantity_decreases_stock(client: AsyncClient, admin_headers):
    created = await client.post(
        "/api/v1/inventory/items",
        json={"name": "Pepper", "quantity": "8.0", "unit": "g"},
        headers=admin_headers,
    )
    item_id = created.json()["data"]["id"]

    response = await client.post(
        f"/api/v1/inventory/items/{item_id}/reduce-quantity",
        json={"amount": "3.0"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    from decimal import Decimal

    assert Decimal(response.json()["data"]["quantity"]) == Decimal("5")


@pytest.mark.asyncio
async def test_reduce_quantity_insufficient_returns_409(client: AsyncClient, admin_headers):
    created = await client.post(
        "/api/v1/inventory/items",
        json={"name": "Cumin", "quantity": "2.0", "unit": "g"},
        headers=admin_headers,
    )
    item_id = created.json()["data"]["id"]

    response = await client.post(
        f"/api/v1/inventory/items/{item_id}/reduce-quantity",
        json={"amount": "5.0"},
        headers=admin_headers,
    )
    assert response.status_code == 409
    assert response.json()["error"] == "CONFLICT"


@pytest.mark.asyncio
async def test_get_nonexistent_item_returns_404(client: AsyncClient, admin_headers):
    response = await client.get(
        "/api/v1/inventory/items/00000000-0000-0000-0000-000000000099",
        headers=admin_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_item_returns_204_and_item_is_gone(client: AsyncClient, admin_headers):
    created = await client.post(
        "/api/v1/inventory/items",
        json={"name": "Paprika", "quantity": "1.0", "unit": "kg"},
        headers=admin_headers,
    )
    item_id = created.json()["data"]["id"]

    delete = await client.delete(f"/api/v1/inventory/items/{item_id}", headers=admin_headers)
    assert delete.status_code == 204

    gone = await client.get(f"/api/v1/inventory/items/{item_id}", headers=admin_headers)
    assert gone.status_code == 404


@pytest.mark.asyncio
async def test_unauthenticated_request_returns_401(client: AsyncClient):
    response = await client.get("/api/v1/inventory/items")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_unit_returns_422(client: AsyncClient, admin_headers):
    response = await client.post(
        "/api/v1/inventory/items",
        json={"name": "X", "quantity": "1.0", "unit": "oz"},
        headers=admin_headers,
    )
    assert response.status_code == 422
