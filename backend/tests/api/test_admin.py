"""
Admin & Audit API Integration Tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_dashboard_stats(client: AsyncClient, admin_token_headers: dict):
    res = await client.get("/api/v1/admin/stats", headers=admin_token_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "total_users" in data
    assert "total_songs" in data
    assert "total_storage_bytes" in data


@pytest.mark.asyncio
async def test_admin_user_management(client: AsyncClient, admin_token_headers: dict, test_user):
    # List users
    res = await client.get("/api/v1/admin/users", headers=admin_token_headers)
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # Toggle role
    res = await client.patch(
        f"/api/v1/admin/users/{test_user.id}/role",
        json={"is_admin": True},
        headers=admin_token_headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["is_admin"] is True


@pytest.mark.asyncio
async def test_admin_audit_logs(client: AsyncClient, admin_token_headers: dict):
    res = await client.get("/api/v1/admin/audit-logs", headers=admin_token_headers)
    assert res.status_code == 200
    assert "meta" in res.json()
