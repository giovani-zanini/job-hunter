"""E2E tests for /api/v1/education/ endpoints.

Covered (CRUD):
    POST   /api/v1/education/        – create education record
    GET    /api/v1/education/        – list education records
    GET    /api/v1/education/{id}    – get by ID
    PUT    /api/v1/education/{id}    – update
    DELETE /api/v1/education/{id}    – soft-delete

Covered (Skills):
    POST   /api/v1/education/{id}/skills/{skill_id}   – add skill
    DELETE /api/v1/education/{id}/skills/{skill_id}   – remove skill
"""

import pytest


pytestmark = pytest.mark.asyncio

BASE = "/api/v1/education"


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


async def create_education(
    client,
    institution: str = "MIT",
    degree: str = "Bachelor",
    field: str = "Computer Science",
) -> dict:
    response = await client.post(
        BASE + "/",
        json={
            "institution_name": institution,
            "degree": degree,
            "field_of_study": field,
            "start_date": "2019-03-01",
            "end_date": "2023-03-01",
            "skill_ids": [],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_skill(client, name: str = "Python") -> dict:
    response = await client.post(
        "/api/v1/skills/",
        json={"name": name, "category": "LANGUAGE"},
    )
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# POST /api/v1/education/
# ---------------------------------------------------------------------------


async def test_create_education_returns_201_with_data(client):
    """Creating an education record returns 201 with all expected fields."""
    response = await client.post(
        BASE + "/",
        json={
            "institution_name": "Stanford University",
            "degree": "Master",
            "field_of_study": "Artificial Intelligence",
            "start_date": "2021-09-01",
            "end_date": "2023-06-01",
            "skill_ids": [],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["institution_name"] == "Stanford University"
    assert body["degree"] == "Master"
    assert body["field_of_study"] == "Artificial Intelligence"
    assert "id" in body
    assert "user_id" in body




async def test_create_education_missing_fields_returns_422(client):
    """Missing required fields returns 422."""
    response = await client.post(
        BASE + "/",
        json={"institution_name": "Only Name"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/education/
# ---------------------------------------------------------------------------


async def test_created_education_appears_in_list(client):
    """An education record created via POST must appear in GET /education/."""
    created = await create_education(client, institution="Cambridge")

    response = await client.get(BASE + "/")

    assert response.status_code == 200
    ids = [e["id"] for e in response.json()]
    assert created["id"] in ids


async def test_list_education_filter_by_institution(client):
    """GET /education/?institution_name=partial returns only matching records."""
    await create_education(client, institution="Harvard University")
    await create_education(client, institution="Oxford University")

    response = await client.get(
        BASE + "/",
        params={"institution_name": "Harvard"},
    )

    assert response.status_code == 200
    items = response.json()
    assert any(e["institution_name"] == "Harvard University" for e in items)
    assert all("Harvard" in e["institution_name"] for e in items)


async def test_list_education_empty_initially(client):
    """GET /education/ returns an empty list when none exist."""
    response = await client.get(BASE + "/")
    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# GET /api/v1/education/{id}
# ---------------------------------------------------------------------------


async def test_created_education_retrievable_by_id(client):
    """An education record created via POST can be fetched by its ID."""
    created = await create_education(client, institution="UC Berkeley")

    response = await client.get(f"{BASE}/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["institution_name"] == "UC Berkeley"


async def test_get_nonexistent_education_returns_404(client):
    """GET /education/999999 returns 404."""
    response = await client.get(f"{BASE}/999999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/v1/education/{id}
# ---------------------------------------------------------------------------


async def test_update_education_changes_values(client):
    """PUT /education/{id} updates degree; GET by id reflects the change."""
    created = await create_education(client, degree="Bachelor")

    put = await client.put(
        f"{BASE}/{created['id']}",
        json={"degree": "PhD", "field_of_study": "Machine Learning"},
    )
    assert put.status_code == 200

    get = await client.get(f"{BASE}/{created['id']}")
    body = get.json()
    assert body["degree"] == "PhD"
    assert body["field_of_study"] == "Machine Learning"


# ---------------------------------------------------------------------------
# DELETE /api/v1/education/{id}
# ---------------------------------------------------------------------------


async def test_delete_education_soft_deletes(client):
    """DELETE /education/{id} soft-deletes; detail with include_deleted shows deleted_at."""
    created = await create_education(
        client, institution="Delete University"
    )

    delete = await client.delete(f"{BASE}/{created['id']}")
    assert delete.status_code == 200

    detail = await client.get(
        f"{BASE}/{created['id']}",
        params={"include_deleted": "true"},
    )
    assert detail.status_code == 200
    assert detail.json()["deleted_at"] is not None


async def test_deleted_education_excluded_from_list(client):
    """Soft-deleted education records do not appear in the default list."""
    created = await create_education(
        client, institution="Gone University"
    )

    await client.delete(f"{BASE}/{created['id']}")

    list_response = await client.get(BASE + "/")
    ids = [e["id"] for e in list_response.json()]
    assert created["id"] not in ids


# ---------------------------------------------------------------------------
# Skill associations
# ---------------------------------------------------------------------------


async def test_add_skill_to_education_returns_201(client):
    """POST /education/{id}/skills/{skill_id} returns 201."""
    education = await create_education(client, institution="Skill Uni")
    skill = await create_skill(client, name="Linear Algebra")

    response = await client.post(
        f"{BASE}/{education['id']}/skills/{skill['id']}",

    )
    assert response.status_code == 201


async def test_remove_skill_from_education_returns_204(client):
    """DELETE /education/{id}/skills/{skill_id} returns 204."""
    education = await create_education(
        client, institution="Remove Skill Uni"
    )
    skill = await create_skill(client, name="Calculus")

    await client.post(
        f"{BASE}/{education['id']}/skills/{skill['id']}",

    )

    delete = await client.delete(
        f"{BASE}/{education['id']}/skills/{skill['id']}",

    )
    assert delete.status_code == 204
