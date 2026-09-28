"""E2E tests for the /health endpoint."""

import pytest


pytestmark = pytest.mark.asyncio


async def test_health_check_returns_healthy(client):
    """GET /health → 200 with status healthy."""
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
