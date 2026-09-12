"""
Auth API Integration Tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # Test Registration
    reg_payload = {
        "email": "newuser@example.com",
        "password": "Password123!",
        "first_name": "New",
        "last_name": "User",
    }
    res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["user"]["email"] == "newuser@example.com"
    assert "tokens" in data
    assert "access_token" in data["tokens"]

    # Test Login
    login_payload = {
        "email": "newuser@example.com",
        "password": "Password123!",
    }
    res = await client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "access_token" in data["tokens"]

    # Test Me Endpoint
    token = data["tokens"]["access_token"]
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["data"]["email"] == "newuser@example.com"
