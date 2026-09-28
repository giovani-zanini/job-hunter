"""E2E tests for /api/v1/requirements/ endpoints."""

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/requirements"


async def create_requirement(client, headers, skill="Python") -> dict:
    response = await client.post(BASE + "/", headers=headers, json={"skill": skill})
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_requirement_returns_201(client, auth_headers):
    response = await client.post(BASE + "/", headers=auth_headers, json={"skill": "FastAPI"})
    assert response.status_code == 201
    body = response.json()
    assert body["skill"] == "FastAPI"
    assert "id" in body


async def test_create_requirement_requires_auth(client):
    response = await client.post(BASE + "/", json={"skill": "Django"})
    assert response.status_code == 401


async def test_create_requirement_missing_skill_returns_422(client, auth_headers):
    response = await client.post(BASE + "/", headers=auth_headers, json={})
    assert response.status_code == 422


async def test_list_requirements_returns_200(client, auth_headers):
    await create_requirement(client, auth_headers)
    response = await client.get(BASE + "/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_requirement_by_id(client, auth_headers):
    created = await create_requirement(client, auth_headers, skill="PostgreSQL")
    response = await client.get(f"{BASE}/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["skill"] == "PostgreSQL"


async def test_get_requirement_not_found_returns_404(client, auth_headers):
    response = await client.get(f"{BASE}/999999", headers=auth_headers)
    assert response.status_code == 404


async def test_update_requirement(client, auth_headers):
    created = await create_requirement(client, auth_headers, skill="OldSkill")
    response = await client.put(
        f"{BASE}/{created['id']}", headers=auth_headers, json={"skill": "NewSkill"}
    )
    assert response.status_code == 200
    assert response.json()["skill"] == "NewSkill"


async def test_delete_requirement_soft_deletes(client, auth_headers):
    created = await create_requirement(client, auth_headers, skill="TempSkill")
    response = await client.delete(f"{BASE}/{created['id']}", headers=auth_headers)
    assert response.status_code == 200

    list_response = await client.get(BASE + "/", headers=auth_headers)
    ids = [r["id"] for r in list_response.json()]
    assert created["id"] not in ids
