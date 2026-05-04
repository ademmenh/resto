"""
E2E tests for auth API endpoints: register, login, refresh.
Covers: success flows, domain errors, cookie setting, RDTO shape.
"""
import pytest
from httpx import AsyncClient


# ── Register ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_returns_201_with_rdto(client: AsyncClient):
    res = await client.post("/api/v1/auth/register", json={
        "name": "Alice",
        "email": "alice.register@e2e.com",
        "password": "secret123",
        "phone": None,
    })
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["statusCode"] == 201
    assert body["message"] == "Registration successful"
    assert "data" in body
    assert body["data"]["email"] == "alice.register@e2e.com"
    assert body["data"]["name"] == "Alice"
    assert body["data"]["role"] == "client"
    assert "id" in body["data"]
    assert "tokens" in body
    assert "accessToken" in body["tokens"]
    assert "refreshToken" in body["tokens"]


@pytest.mark.asyncio
async def test_register_sets_auth_cookies(client: AsyncClient):
    res = await client.post("/api/v1/auth/register", json={
        "name": "Cookie User",
        "email": "cookie.user@e2e.com",
        "password": "pass",
        "phone": None,
    })
    assert res.status_code == 201
    assert "access_token" in res.cookies
    assert "refresh_token" in res.cookies


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client: AsyncClient):
    payload = {"name": "Dup", "email": "dup@e2e.com", "password": "pass"}
    await client.post("/api/v1/auth/register", json=payload)
    client.cookies.clear()
    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 409
    assert res.json()["error"] == "CONFLICT"


@pytest.mark.asyncio
async def test_register_invalid_email_returns_422(client: AsyncClient):
    res = await client.post("/api/v1/auth/register", json={
        "name": "X",
        "email": "not-an-email",
        "password": "pass",
    })
    assert res.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_returns_200_with_rdto(client: AsyncClient):
    email = "login.user@e2e.com"
    await client.post("/api/v1/auth/register", json={"name": "LoginUser", "email": email, "password": "mypassword"})
    client.cookies.clear()
    res = await client.post("/api/v1/auth/login", json={"email": email, "password": "mypassword"})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["statusCode"] == 200
    assert body["message"] == "Login successful"
    assert body["data"]["email"] == email
    assert "tokens" in body
    assert "accessToken" in body["tokens"]


@pytest.mark.asyncio
async def test_login_sets_auth_cookies(client: AsyncClient):
    email = "cookie.login@e2e.com"
    await client.post("/api/v1/auth/register", json={"name": "CL", "email": email, "password": "pass"})
    client.cookies.clear()
    res = await client.post("/api/v1/auth/login", json={"email": email, "password": "pass"})
    assert res.status_code == 200
    assert "access_token" in res.cookies
    assert "refresh_token" in res.cookies


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client: AsyncClient):
    email = "wrong.pass@e2e.com"
    await client.post("/api/v1/auth/register", json={"name": "WP", "email": email, "password": "correct"})
    client.cookies.clear()
    res = await client.post("/api/v1/auth/login", json={"email": email, "password": "wrong"})
    assert res.status_code == 401
    assert res.json()["error"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401(client: AsyncClient):
    res = await client.post("/api/v1/auth/login", json={"email": "nobody@e2e.com", "password": "pass"})
    assert res.status_code == 401
    assert res.json()["error"] == "UNAUTHORIZED"


# ── Refresh ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refresh_returns_new_tokens(client: AsyncClient):
    res = await client.post("/api/v1/auth/register", json={
        "name": "Refresh User",
        "email": "refresh@e2e.com",
        "password": "pass",
    })
    refresh_token = res.json()["tokens"]["refreshToken"]
    # Clear cookies to use Bearer header only
    client.cookies.clear()
    res = await client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["statusCode"] == 200
    assert body["message"] == "Token refreshed"
    assert "accessToken" in body["data"]
    assert "refreshToken" in body["data"]


@pytest.mark.asyncio
async def test_refresh_with_invalid_token_returns_401(client: AsyncClient):
    res = await client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert res.status_code == 401
