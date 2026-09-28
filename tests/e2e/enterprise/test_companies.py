"""E2E tests for /api/v1/enterprise/companies/ endpoints."""

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/enterprise/companies"


async def create_company(client, headers, name="Acme Enterprise") -> dict:
    response = await client.post(BASE + "/", headers=headers, json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


async def create_location(client, headers) -> dict:
    response = await client.post(
        "/api/v1/locations/", headers=headers, json={"country": "BR", "state": "SP"}
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_segment(client, headers, name="Tech") -> dict:
    response = await client.post(
        "/api/v1/segments/", headers=headers, json={"name": name}
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_company_returns_201(client, auth_headers):
    response = await client.post(
        BASE + "/", headers=auth_headers, json={"name": "TechCorp"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "TechCorp"
    assert "id" in body


async def test_create_company_requires_auth(client):
    response = await client.post(BASE + "/", json={"name": "Ghost"})
    assert response.status_code == 401


async def test_list_companies_returns_200(client, auth_headers):
    await create_company(client, auth_headers)
    response = await client.get(BASE + "/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_company_by_id(client, auth_headers):
    created = await create_company(client, auth_headers, name="GetMe Corp")
    response = await client.get(f"{BASE}/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "GetMe Corp"


async def test_get_company_not_found_returns_404(client, auth_headers):
    response = await client.get(f"{BASE}/999999", headers=auth_headers)
    assert response.status_code == 404


async def test_update_company(client, auth_headers):
    created = await create_company(client, auth_headers, name="OldName")
    response = await client.put(
        f"{BASE}/{created['id']}", headers=auth_headers, json={"name": "NewName"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "NewName"


async def test_delete_company_soft_deletes(client, auth_headers):
    created = await create_company(client, auth_headers)
    response = await client.delete(f"{BASE}/{created['id']}", headers=auth_headers)
    assert response.status_code == 200

    list_response = await client.get(BASE + "/", headers=auth_headers)
    ids = [c["id"] for c in list_response.json()]
    assert created["id"] not in ids


async def test_add_unit_to_company(client, auth_headers):
    company = await create_company(client, auth_headers)
    location = await create_location(client, auth_headers)

    response = await client.post(
        f"{BASE}/{company['id']}/units",
        headers=auth_headers,
        json={"location_id": location["id"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["company_id"] == company["id"]
    assert body["location_id"] == location["id"]


async def test_add_segment_to_company(client, auth_headers):
    company = await create_company(client, auth_headers)
    segment = await create_segment(client, auth_headers, name="SegX")

    response = await client.post(
        f"{BASE}/{company['id']}/segments",
        headers=auth_headers,
        json={"segment_id": segment["id"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["company_id"] == company["id"]
    assert body["segment_id"] == segment["id"]
