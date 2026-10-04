"""E2E tests for /api/v1/locations/ endpoints."""

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/locations"


async def create_location(client, country="BR", state="SP", city="São Paulo") -> dict:
    response = await client.post(
        BASE + "/",
        json={"country": country, "state": state, "city": city},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_location_returns_201(client):
    response = await client.post(
        BASE + "/", json={"country": "BR", "state": "SP", "city": "Campinas"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["country"] == "BR"
    assert body["state"] == "SP"
    assert body["city"] == "Campinas"
    assert "id" in body




async def test_create_location_missing_required_fields_returns_422(client):
    response = await client.post(BASE + "/", json={"city": "São Paulo"})
    assert response.status_code == 422


async def test_list_locations_returns_200(client):
    await create_location(client)
    response = await client.get(BASE + "/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


async def test_created_location_appears_in_list(client):
    created = await create_location(client, city="UniqueCity123")
    response = await client.get(BASE + "/")
    ids = [loc["id"] for loc in response.json()]
    assert created["id"] in ids


async def test_get_location_by_id(client):
    created = await create_location(client)
    response = await client.get(f"{BASE}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_get_location_not_found_returns_404(client):
    response = await client.get(f"{BASE}/999999")
    assert response.status_code == 404


async def test_update_location(client):
    created = await create_location(client, city="OldCity")
    response = await client.put(
        f"{BASE}/{created['id']}", json={"city": "NewCity"}
    )
    assert response.status_code == 200
    assert response.json()["city"] == "NewCity"


async def test_delete_location_soft_deletes(client):
    created = await create_location(client)
    response = await client.delete(f"{BASE}/{created['id']}")
    assert response.status_code == 200

    # No longer in default list
    list_response = await client.get(BASE + "/")
    ids = [loc["id"] for loc in list_response.json()]
    assert created["id"] not in ids

    # Visible with include_deleted
    list_deleted = await client.get(BASE + "/", params={"include_deleted": True})
    ids_with_deleted = [loc["id"] for loc in list_deleted.json()]
    assert created["id"] in ids_with_deleted
