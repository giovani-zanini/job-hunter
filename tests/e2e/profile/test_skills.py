"""E2E tests for /api/v1/skills/ endpoints.

Covered:
    POST   /api/v1/skills/            – create skill
    GET    /api/v1/skills/            – list skills (+ filters)
    GET    /api/v1/skills/{id}        – get skill by ID
    PUT    /api/v1/skills/{id}        – update skill
    DELETE /api/v1/skills/{id}        – soft-delete skill
"""

import pytest


pytestmark = pytest.mark.asyncio

BASE = "/api/v1/skills"


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


async def create_skill(client, name="Python", category="LANGUAGE") -> dict:
    """Helper: POST a skill and return the response body."""
    response = await client.post(
        BASE + "/", json={"name": name, "category": category}
    )
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# POST /api/v1/skills/
# ---------------------------------------------------------------------------


async def test_create_skill_returns_201_with_data(client):
    """Creating a skill returns 201 with id, name and category."""
    response = await client.post(
        BASE + "/",
        json={"name": "Python", "category": "LANGUAGE"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Python"
    assert body["category"] == "LANGUAGE"
    assert "id" in body




async def test_create_skill_invalid_category_returns_422(client):
    """Invalid category value returns 422 Unprocessable Entity."""
    response = await client.post(
        BASE + "/",
        json={"name": "Python", "category": "INVALID_CATEGORY"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/skills/ — the core E2E verification
# ---------------------------------------------------------------------------


async def test_created_skill_appears_in_list(client):
    """A skill created via POST /skills/ must appear in GET /skills/."""
    created = await create_skill(client, name="Go", category="LANGUAGE")

    response = await client.get(BASE + "/")

    assert response.status_code == 200
    ids = [s["id"] for s in response.json()]
    assert created["id"] in ids


async def test_list_skills_filter_by_name(client):
    """GET /skills/?name=<partial> returns only matching skills."""
    await create_skill(client, name="TypeScript", category="LANGUAGE")
    await create_skill(client, name="JavaScript", category="LANGUAGE")

    response = await client.get(
        BASE + "/", params={"name": "Script"}
    )

    assert response.status_code == 200
    names = [s["name"] for s in response.json()]
    assert "TypeScript" in names
    assert "JavaScript" in names


async def test_list_skills_filter_by_category(client):
    """GET /skills/?category=TOOL returns only TOOL-category skills."""
    await create_skill(client, name="Docker", category="TOOL")
    await create_skill(client, name="Kotlin", category="LANGUAGE")

    response = await client.get(
        BASE + "/", params={"category": "TOOL"}
    )

    assert response.status_code == 200
    items = response.json()
    assert all(s["category"] == "TOOL" for s in items)
    assert any(s["name"] == "Docker" for s in items)


async def test_list_skills_empty_when_no_skills(client):
    """GET /skills/ returns an empty list when no skills have been created."""
    response = await client.get(BASE + "/")
    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# GET /api/v1/skills/{id}
# ---------------------------------------------------------------------------


async def test_created_skill_retrievable_by_id(client):
    """A skill created via POST can be fetched by its ID from GET /skills/{id}."""
    created = await create_skill(client, name="Rust", category="LANGUAGE")

    response = await client.get(f"{BASE}/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["name"] == "Rust"
    assert body["category"] == "LANGUAGE"


async def test_get_nonexistent_skill_returns_404(client):
    """GET /skills/{id} for a non-existent id returns 404."""
    response = await client.get(f"{BASE}/999999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/v1/skills/{id}
# ---------------------------------------------------------------------------


async def test_update_skill_changes_values(client):
    """PUT /skills/{id} updates name and category; GET by id reflects the change."""
    created = await create_skill(client, name="Java", category="LANGUAGE")

    put_response = await client.put(
        f"{BASE}/{created['id']}",
        json={"name": "Java (Updated)", "category": "FRAMEWORK"},
    )
    assert put_response.status_code == 200

    get_response = await client.get(f"{BASE}/{created['id']}")
    body = get_response.json()
    assert body["name"] == "Java (Updated)"
    assert body["category"] == "FRAMEWORK"


async def test_update_nonexistent_skill_returns_404(client):
    """PUT /skills/999999 returns 404."""
    response = await client.put(
        f"{BASE}/999999",
        json={"name": "Ghost"},
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/skills/{id}
# ---------------------------------------------------------------------------


async def test_delete_skill_sets_deleted_at(client):
    """DELETE /skills/{id} soft-deletes; response contains deleted_at timestamp."""
    created = await create_skill(
        client, name="Scala", category="LANGUAGE"
    )

    delete_response = await client.delete(
        f"{BASE}/{created['id']}"
    )
    assert delete_response.status_code == 200

    # The DELETE response itself contains the deleted record with deleted_at set
    assert delete_response.json()["deleted_at"] is not None


async def test_deleted_skill_excluded_from_list(client):
    """Soft-deleted skills do not appear in the default GET /skills/ response."""
    created = await create_skill(
        client, name="Elixir", category="LANGUAGE"
    )

    await client.delete(f"{BASE}/{created['id']}")

    list_response = await client.get(BASE + "/")
    assert list_response.status_code == 200
    ids = [s["id"] for s in list_response.json()]
    assert created["id"] not in ids
