"""E2E tests for /api/v1/responsabilities/ endpoints."""

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/responsabilities"

PAYLOAD = {"action": "develop", "target": "backend services", "outcome": "stable APIs"}


async def create_responsability(client, **overrides) -> dict:
    payload = {**PAYLOAD, **overrides}
    response = await client.post(BASE + "/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_responsability_returns_201(client):
    response = await client.post(BASE + "/", json=PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["action"] == "develop"
    assert "id" in body




async def test_create_responsability_missing_fields_returns_422(client):
    response = await client.post(BASE + "/", json={"action": "only"})
    assert response.status_code == 422


async def test_list_responsabilities_returns_200(client):
    await create_responsability(client)
    response = await client.get(BASE + "/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_responsability_by_id(client):
    created = await create_responsability(client)
    response = await client.get(f"{BASE}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_get_responsability_not_found_returns_404(client):
    response = await client.get(f"{BASE}/999999")
    assert response.status_code == 404


async def test_update_responsability(client):
    created = await create_responsability(client)
    response = await client.put(
        f"{BASE}/{created['id']}", json={"action": "maintain"}
    )
    assert response.status_code == 200
    assert response.json()["action"] == "maintain"


async def test_delete_responsability_soft_deletes(client):
    created = await create_responsability(client)
    response = await client.delete(f"{BASE}/{created['id']}")
    assert response.status_code == 200

    list_response = await client.get(BASE + "/")
    ids = [r["id"] for r in list_response.json()]
    assert created["id"] not in ids
