"""E2E tests for /api/v1/vacancies/ endpoints."""

from datetime import date

import pytest

pytestmark = pytest.mark.asyncio

BASE = "/api/v1/vacancies"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_location(client, headers) -> int:
    r = await client.post(
        "/api/v1/locations/", headers=headers, json={"country": "BR", "state": "SP"}
    )
    assert r.status_code == 201
    return r.json()["id"]


async def _create_company(client, headers) -> int:
    r = await client.post(
        "/api/v1/enterprise/companies/", headers=headers, json={"name": "VacancyCorp"}
    )
    assert r.status_code == 201
    return r.json()["id"]


async def _create_unit(client, headers, company_id: int, location_id: int) -> int:
    r = await client.post(
        f"/api/v1/enterprise/companies/{company_id}/units",
        headers=headers,
        json={"location_id": location_id},
    )
    assert r.status_code == 201
    return r.json()["id"]


async def _create_requirement(client, headers, skill="Python") -> int:
    r = await client.post(
        "/api/v1/requirements/", headers=headers, json={"skill": skill}
    )
    assert r.status_code == 201
    return r.json()["id"]


async def _create_responsability(client, headers) -> int:
    r = await client.post(
        "/api/v1/responsabilities/",
        headers=headers,
        json={"action": "build", "target": "features", "outcome": "value"},
    )
    assert r.status_code == 201
    return r.json()["id"]


async def _setup_unit(client, auth_headers) -> int:
    location_id = await _create_location(client, auth_headers)
    company_id = await _create_company(client, auth_headers)
    return await _create_unit(client, auth_headers, company_id, location_id)


async def create_vacancy(
    client, headers, unit_id: int, title="Backend Developer"
) -> dict:
    response = await client.post(
        BASE + "/",
        headers=headers,
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


async def test_create_vacancy_returns_201(client, auth_headers):
    unit_id = await _setup_unit(client, auth_headers)
    response = await client.post(
        BASE + "/",
        headers=auth_headers,
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


async def test_create_vacancy_requires_auth(client):
    response = await client.post(
        BASE + "/",
        json={
            "title": "Ghost Dev",
            "description": "...",
            "company_unit_id": 1,
            "seniority_level": "JUNIOR",
            "published_date": str(date.today()),
        },
    )
    assert response.status_code == 401


async def test_list_vacancies_returns_200(client, auth_headers):
    unit_id = await _setup_unit(client, auth_headers)
    await create_vacancy(client, auth_headers, unit_id)

    response = await client.get(BASE + "/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_get_vacancy_by_id_includes_associations(client, auth_headers):
    unit_id = await _setup_unit(client, auth_headers)
    created = await create_vacancy(client, auth_headers, unit_id)

    response = await client.get(f"{BASE}/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert "vacancy_requirements" in body
    assert "vacancy_responsabilities" in body


async def test_get_vacancy_not_found_returns_404(client, auth_headers):
    response = await client.get(f"{BASE}/999999", headers=auth_headers)
    assert response.status_code == 404


async def test_update_vacancy(client, auth_headers):
    unit_id = await _setup_unit(client, auth_headers)
    created = await create_vacancy(client, auth_headers, unit_id)
    response = await client.put(
        f"{BASE}/{created['id']}", headers=auth_headers, json={"title": "Updated Dev"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Dev"


async def test_delete_vacancy_soft_deletes(client, auth_headers):
    unit_id = await _setup_unit(client, auth_headers)
    created = await create_vacancy(client, auth_headers, unit_id)
    response = await client.delete(f"{BASE}/{created['id']}", headers=auth_headers)
    assert response.status_code == 200

    list_response = await client.get(BASE + "/", headers=auth_headers)
    ids = [v["id"] for v in list_response.json()]
    assert created["id"] not in ids


async def test_add_requirement_to_vacancy(client, auth_headers):
    unit_id = await _setup_unit(client, auth_headers)
    vacancy = await create_vacancy(client, auth_headers, unit_id)
    req_id = await _create_requirement(client, auth_headers, skill="Django")

    response = await client.post(
        f"{BASE}/{vacancy['id']}/requirements",
        headers=auth_headers,
        json={"requirement_id": req_id, "level": 3, "requirement_type": "MANDATORY"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["requirement_id"] == req_id
    assert body["vacancy_id"] == vacancy["id"]


async def test_remove_requirement_from_vacancy(client, auth_headers):
    unit_id = await _setup_unit(client, auth_headers)
    vacancy = await create_vacancy(client, auth_headers, unit_id)
    req_id = await _create_requirement(client, auth_headers, skill="Golang")

    add_response = await client.post(
        f"{BASE}/{vacancy['id']}/requirements",
        headers=auth_headers,
        json={"requirement_id": req_id, "level": 2, "requirement_type": "OPTIONAL"},
    )
    vr_id = add_response.json()["id"]

    delete_response = await client.delete(
        f"{BASE}/{vacancy['id']}/requirements/{vr_id}", headers=auth_headers
    )
    assert delete_response.status_code == 204


async def test_add_responsability_to_vacancy(client, auth_headers):
    unit_id = await _setup_unit(client, auth_headers)
    vacancy = await create_vacancy(client, auth_headers, unit_id)
    resp_id = await _create_responsability(client, auth_headers)

    response = await client.post(
        f"{BASE}/{vacancy['id']}/responsabilities",
        headers=auth_headers,
        json={"responsability_id": resp_id},
    )
    assert response.status_code == 201
    assert response.json()["responsability_id"] == resp_id


async def test_add_duplicate_responsability_returns_409(client, auth_headers):
    unit_id = await _setup_unit(client, auth_headers)
    vacancy = await create_vacancy(client, auth_headers, unit_id)
    resp_id = await _create_responsability(client, auth_headers)

    await client.post(
        f"{BASE}/{vacancy['id']}/responsabilities",
        headers=auth_headers,
        json={"responsability_id": resp_id},
    )
    response = await client.post(
        f"{BASE}/{vacancy['id']}/responsabilities",
        headers=auth_headers,
        json={"responsability_id": resp_id},
    )
    assert response.status_code == 409
