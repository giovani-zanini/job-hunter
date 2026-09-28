"""E2E tests for /api/v1/segments/ endpoints."""

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/segments"


async def create_segment(client, headers, name="Technology") -> dict:
    response = await client.post(BASE + "/", headers=headers, json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_segment_returns_201(client, auth_headers):
    response = await client.post(BASE + "/", headers=auth_headers, json={"name": "Finance"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Finance"
    assert "id" in body


async def test_create_segment_requires_auth(client):
    response = await client.post(BASE + "/", json={"name": "Stealth"})
    assert response.status_code == 401


async def test_create_segment_missing_name_returns_422(client, auth_headers):
    response = await client.post(BASE + "/", headers=auth_headers, json={})
    assert response.status_code == 422


async def test_list_segments_returns_200(client, auth_headers):
    await create_segment(client, auth_headers)
    response = await client.get(BASE + "/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_segment_by_id(client, auth_headers):
    created = await create_segment(client, auth_headers, name="Healthcare")
    response = await client.get(f"{BASE}/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Healthcare"


async def test_get_segment_not_found_returns_404(client, auth_headers):
    response = await client.get(f"{BASE}/999999", headers=auth_headers)
    assert response.status_code == 404


async def test_update_segment(client, auth_headers):
    created = await create_segment(client, auth_headers, name="OldName")
    response = await client.put(f"{BASE}/{created['id']}", headers=auth_headers, json={"name": "NewName"})
    assert response.status_code == 200
    assert response.json()["name"] == "NewName"


async def test_delete_segment_soft_deletes(client, auth_headers):
    created = await create_segment(client, auth_headers, name="ToDelete")
    delete_response = await client.delete(f"{BASE}/{created['id']}", headers=auth_headers)
    assert delete_response.status_code == 200

    list_response = await client.get(BASE + "/", headers=auth_headers)
    ids = [s["id"] for s in list_response.json()]
    assert created["id"] not in ids
