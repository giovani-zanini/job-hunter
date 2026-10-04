"""E2E tests for /api/v1/contracts/ endpoints."""

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/contracts"

CONTRACT_PAYLOAD = {
    "type": "CLT",
    "regional_classification": "BRL",
    "currency": "BRL",
    "payment_periodicity": "MONTHLY",
    "min_payment_amount": 3000,
    "max_payment_amount": 6000,
    "is_payment_disclosed": True,
}


async def create_contract(client, **overrides) -> dict:
    payload = {**CONTRACT_PAYLOAD, **overrides}
    response = await client.post(BASE + "/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_contract_returns_201(client):
    response = await client.post(
        BASE + "/", json=CONTRACT_PAYLOAD
    )
    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "CLT"
    assert body["currency"] == "BRL"
    assert "id" in body




async def test_create_contract_missing_fields_returns_422(client):
    response = await client.post(BASE + "/", json={})
    assert response.status_code == 422


async def test_list_contracts_returns_200(client):
    await create_contract(client)
    response = await client.get(BASE + "/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_contract_by_id(client):
    created = await create_contract(client)
    response = await client.get(f"{BASE}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_get_contract_not_found_returns_404(client):
    response = await client.get(f"{BASE}/999999")
    assert response.status_code == 404


async def test_update_contract(client):
    created = await create_contract(client)
    response = await client.put(
        f"{BASE}/{created['id']}", json={"type": "PJ"}
    )
    assert response.status_code == 200
    assert response.json()["type"] == "PJ"


async def test_delete_contract_soft_deletes(client):
    created = await create_contract(client)
    response = await client.delete(f"{BASE}/{created['id']}")
    assert response.status_code == 200

    list_response = await client.get(BASE + "/")
    ids = [c["id"] for c in list_response.json()]
    assert created["id"] not in ids
