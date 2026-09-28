"""E2E tests for /api/v1/metas/ endpoints."""

from datetime import datetime, timezone

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/metas"
NOW = datetime.now(timezone.utc).isoformat()

META_PAYLOAD = {
    "app_version": "1.0.0",
    "extraction_timestamp": NOW,
    "parsing_timestamp": NOW,
    "source_url": "https://jobs.example.com/123",
}


async def create_meta(client, headers, **overrides) -> dict:
    payload = {**META_PAYLOAD, **overrides}
    response = await client.post(BASE + "/", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_meta_returns_201(client, auth_headers):
    response = await client.post(BASE + "/", headers=auth_headers, json=META_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["app_version"] == "1.0.0"
    assert body["source_url"] == "https://jobs.example.com/123"
    assert "id" in body


async def test_create_meta_requires_auth(client):
    response = await client.post(BASE + "/", json=META_PAYLOAD)
    assert response.status_code == 401


async def test_create_meta_missing_required_fields_returns_422(client, auth_headers):
    response = await client.post(BASE + "/", headers=auth_headers, json={"app_version": "1.0.0"})
    assert response.status_code == 422


async def test_list_metas_returns_200(client, auth_headers):
    await create_meta(client, auth_headers)
    response = await client.get(BASE + "/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_meta_by_id(client, auth_headers):
    created = await create_meta(client, auth_headers)
    response = await client.get(f"{BASE}/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_get_meta_not_found_returns_404(client, auth_headers):
    response = await client.get(f"{BASE}/999999", headers=auth_headers)
    assert response.status_code == 404


async def test_update_meta(client, auth_headers):
    created = await create_meta(client, auth_headers)
    response = await client.put(
        f"{BASE}/{created['id']}",
        headers=auth_headers,
        json={"source_url": "https://updated.example.com/456"},
    )
    assert response.status_code == 200
    assert response.json()["source_url"] == "https://updated.example.com/456"


async def test_delete_meta_soft_deletes(client, auth_headers):
    created = await create_meta(client, auth_headers)
    response = await client.delete(f"{BASE}/{created['id']}", headers=auth_headers)
    assert response.status_code == 200

    list_response = await client.get(BASE + "/", headers=auth_headers)
    ids = [m["id"] for m in list_response.json()]
    assert created["id"] not in ids


async def test_filter_metas_by_vacancy_id(client, auth_headers):
    await create_meta(client, auth_headers, vacancy_id=None)
    response = await client.get(BASE + "/", headers=auth_headers, params={"vacancy_id": 99999})
    assert response.status_code == 200
    assert response.json() == []
