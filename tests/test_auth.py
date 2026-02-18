from __future__ import annotations

from httpx import AsyncClient


async def test_login_success(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "attorney@alma.com", "password": "password123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_login_invalid_credentials(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "attorney@alma.com", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"
