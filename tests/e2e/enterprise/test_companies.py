"""E2E tests for /api/v1/enterprise/companies/ endpoints."""

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/enterprise/companies"


async def create_company(client, name="Acme Enterprise") -> dict:
    response = await client.post(BASE + "/", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


async def create_location(client) -> dict:
    response = await client.post(
        "/api/v1/locations/", json={"country": "BR", "state": "SP"}
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_segment(client, name="Tech") -> dict:
    response = await client.post(
        "/api/v1/segments/", json={"name": name}
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_company_returns_201(client):
    response = await client.post(
        BASE + "/", json={"name": "TechCorp"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "TechCorp"
    assert "id" in body




async def test_list_companies_returns_200(client):
    await create_company(client)
    response = await client.get(BASE + "/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_company_by_id(client):
    created = await create_company(client, name="GetMe Corp")
    response = await client.get(f"{BASE}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "GetMe Corp"


async def test_get_company_not_found_returns_404(client):
    response = await client.get(f"{BASE}/999999")
    assert response.status_code == 404


async def test_update_company(client):
    created = await create_company(client, name="OldName")
    response = await client.put(
        f"{BASE}/{created['id']}", json={"name": "NewName"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "NewName"


async def test_delete_company_soft_deletes(client):
    created = await create_company(client)
    response = await client.delete(f"{BASE}/{created['id']}")
    assert response.status_code == 200

    list_response = await client.get(BASE + "/")
    ids = [c["id"] for c in list_response.json()]
    assert created["id"] not in ids


async def test_add_unit_to_company(client):
    company = await create_company(client)
    location = await create_location(client)

    response = await client.post(
        f"{BASE}/{company['id']}/units",
        json={"location_id": location["id"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["company_id"] == company["id"]
    assert body["location_id"] == location["id"]


async def test_add_segment_to_company(client):
    company = await create_company(client)
    segment = await create_segment(client, name="SegX")

    response = await client.post(
        f"{BASE}/{company['id']}/segments",
        json={"segment_id": segment["id"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["company_id"] == company["id"]
    assert body["segment_id"] == segment["id"]
