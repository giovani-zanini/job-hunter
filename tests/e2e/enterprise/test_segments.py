"""E2E tests for /api/v1/segments/ endpoints."""

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/segments"


async def create_segment(client, name="Technology") -> dict:
    response = await client.post(BASE + "/", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_segment_returns_201(client):
    response = await client.post(BASE + "/", json={"name": "Finance"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Finance"
    assert "id" in body




async def test_create_segment_missing_name_returns_422(client):
    response = await client.post(BASE + "/", json={})
    assert response.status_code == 422


async def test_list_segments_returns_200(client):
    await create_segment(client)
    response = await client.get(BASE + "/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_segment_by_id(client):
    created = await create_segment(client, name="Healthcare")
    response = await client.get(f"{BASE}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Healthcare"


async def test_get_segment_not_found_returns_404(client):
    response = await client.get(f"{BASE}/999999")
    assert response.status_code == 404


async def test_update_segment(client):
    created = await create_segment(client, name="OldName")
    response = await client.put(f"{BASE}/{created['id']}", json={"name": "NewName"})
    assert response.status_code == 200
    assert response.json()["name"] == "NewName"


async def test_delete_segment_soft_deletes(client):
    created = await create_segment(client, name="ToDelete")
    delete_response = await client.delete(f"{BASE}/{created['id']}")
    assert delete_response.status_code == 200

    list_response = await client.get(BASE + "/")
    ids = [s["id"] for s in list_response.json()]
    assert created["id"] not in ids
