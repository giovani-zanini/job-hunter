"""E2E tests for /api/v1/requirements/ endpoints."""

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/requirements"


async def create_requirement(client, skill="Python") -> dict:
    response = await client.post(BASE + "/", json={"skill": skill})
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_requirement_returns_201(client):
    response = await client.post(BASE + "/", json={"skill": "FastAPI"})
    assert response.status_code == 201
    body = response.json()
    assert body["skill"] == "FastAPI"
    assert "id" in body




async def test_create_requirement_missing_skill_returns_422(client):
    response = await client.post(BASE + "/", json={})
    assert response.status_code == 422


async def test_list_requirements_returns_200(client):
    await create_requirement(client)
    response = await client.get(BASE + "/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_requirement_by_id(client):
    created = await create_requirement(client, skill="PostgreSQL")
    response = await client.get(f"{BASE}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["skill"] == "PostgreSQL"


async def test_get_requirement_not_found_returns_404(client):
    response = await client.get(f"{BASE}/999999")
    assert response.status_code == 404


async def test_update_requirement(client):
    created = await create_requirement(client, skill="OldSkill")
    response = await client.put(
        f"{BASE}/{created['id']}", json={"skill": "NewSkill"}
    )
    assert response.status_code == 200
    assert response.json()["skill"] == "NewSkill"


async def test_delete_requirement_soft_deletes(client):
    created = await create_requirement(client, skill="TempSkill")
    response = await client.delete(f"{BASE}/{created['id']}")
    assert response.status_code == 200

    list_response = await client.get(BASE + "/")
    ids = [r["id"] for r in list_response.json()]
    assert created["id"] not in ids
