"""E2E tests for /api/v1/vacancies/ endpoints."""

from datetime import date

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/vacancies"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_location(client) -> int:
    r = await client.post(
        "/api/v1/locations/", json={"country": "BR", "state": "SP"}
    )
    assert r.status_code == 201
    return r.json()["id"]


async def _create_company(client) -> int:
    r = await client.post(
        "/api/v1/enterprise/companies/", json={"name": "VacancyCorp"}
    )
    assert r.status_code == 201
    return r.json()["id"]


async def _create_unit(client, company_id: int, location_id: int) -> int:
    r = await client.post(
        f"/api/v1/enterprise/companies/{company_id}/units",
        json={"location_id": location_id},
    )
    assert r.status_code == 201
    return r.json()["id"]


async def _create_requirement(client, skill="Python") -> int:
    r = await client.post(
        "/api/v1/requirements/", json={"skill": skill}
    )
    assert r.status_code == 201
    return r.json()["id"]


async def _create_responsability(client) -> int:
    r = await client.post(
        "/api/v1/responsabilities/",
        json={"action": "build", "target": "features", "outcome": "value"},
    )
    assert r.status_code == 201
    return r.json()["id"]


async def _setup_unit(client) -> int:
    location_id = await _create_location(client)
    company_id = await _create_company(client)
    return await _create_unit(client, company_id, location_id)


async def create_vacancy(
    client, unit_id: int, title="Backend Developer"
) -> dict:
    response = await client.post(
        BASE + "/",
        json={
            "title": title,
            "description": "Build and maintain APIs",
            "company_unit_id": unit_id,
            "seniority_level": "MID",
            "published_date": str(date.today()),
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_create_vacancy_returns_201(client):
    unit_id = await _setup_unit(client)
    response = await client.post(
        BASE + "/",
        json={
            "title": "Backend Dev",
            "description": "Build APIs",
            "company_unit_id": unit_id,
            "seniority_level": "SENIOR",
            "published_date": str(date.today()),
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Backend Dev"
    assert "id" in body




async def test_list_vacancies_returns_200(client):
    unit_id = await _setup_unit(client)
    await create_vacancy(client, unit_id)

    response = await client.get(BASE + "/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_vacancy_by_id_includes_associations(client):
    unit_id = await _setup_unit(client)
    created = await create_vacancy(client, unit_id)

    response = await client.get(f"{BASE}/{created['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert "vacancy_requirements" in body
    assert "vacancy_responsabilities" in body


async def test_get_vacancy_not_found_returns_404(client):
    response = await client.get(f"{BASE}/999999")
    assert response.status_code == 404


async def test_update_vacancy(client):
    unit_id = await _setup_unit(client)
    created = await create_vacancy(client, unit_id)
    response = await client.put(
        f"{BASE}/{created['id']}", json={"title": "Updated Dev"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Dev"


async def test_delete_vacancy_soft_deletes(client):
    unit_id = await _setup_unit(client)
    created = await create_vacancy(client, unit_id)
    response = await client.delete(f"{BASE}/{created['id']}")
    assert response.status_code == 200

    list_response = await client.get(BASE + "/")
    ids = [v["id"] for v in list_response.json()]
    assert created["id"] not in ids


async def test_add_requirement_to_vacancy(client):
    unit_id = await _setup_unit(client)
    vacancy = await create_vacancy(client, unit_id)
    req_id = await _create_requirement(client, skill="Django")

    response = await client.post(
        f"{BASE}/{vacancy['id']}/requirements",
        json={"requirement_id": req_id, "level": 3, "requirement_type": "MANDATORY"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["requirement_id"] == req_id
    assert body["vacancy_id"] == vacancy["id"]


async def test_remove_requirement_from_vacancy(client):
    unit_id = await _setup_unit(client)
    vacancy = await create_vacancy(client, unit_id)
    req_id = await _create_requirement(client, skill="Golang")

    add_response = await client.post(
        f"{BASE}/{vacancy['id']}/requirements",
        json={"requirement_id": req_id, "level": 2, "requirement_type": "OPTIONAL"},
    )
    vr_id = add_response.json()["id"]

    delete_response = await client.delete(
        f"{BASE}/{vacancy['id']}/requirements/{vr_id}"
    )
    assert delete_response.status_code == 204


async def test_add_responsability_to_vacancy(client):
    unit_id = await _setup_unit(client)
    vacancy = await create_vacancy(client, unit_id)
    resp_id = await _create_responsability(client)

    response = await client.post(
        f"{BASE}/{vacancy['id']}/responsabilities",
        json={"responsability_id": resp_id},
    )
    assert response.status_code == 201
    assert response.json()["responsability_id"] == resp_id


async def test_add_duplicate_responsability_returns_409(client):
    unit_id = await _setup_unit(client)
    vacancy = await create_vacancy(client, unit_id)
    resp_id = await _create_responsability(client)

    await client.post(
        f"{BASE}/{vacancy['id']}/responsabilities",
        json={"responsability_id": resp_id},
    )
    response = await client.post(
        f"{BASE}/{vacancy['id']}/responsabilities",
        json={"responsability_id": resp_id},
    )
    assert response.status_code == 409
