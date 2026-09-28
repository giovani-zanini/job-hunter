"""E2E tests for /api/v1/experiences/ endpoints.

Covered (CRUD):
    POST   /api/v1/experiences/           – create experience
    GET    /api/v1/experiences/           – list experiences
    GET    /api/v1/experiences/{id}       – get experience by ID
    PUT    /api/v1/experiences/{id}       – update experience
    DELETE /api/v1/experiences/{id}       – soft-delete experience

Covered (Achievements):
    POST   /api/v1/experiences/{id}/achievements          – add achievement
    PUT    /api/v1/experiences/achievements/{ach_id}      – update achievement
    DELETE /api/v1/experiences/achievements/{ach_id}      – remove achievement

Covered (Skills):
    POST   /api/v1/experiences/{id}/skills/{skill_id}     – add skill to experience
    DELETE /api/v1/experiences/{id}/skills/{skill_id}     – remove skill from experience
"""

import pytest


pytestmark = pytest.mark.asyncio

BASE = "/api/v1/experiences"


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


async def create_company(client, headers, name: str = "Acme Corp") -> dict:
    response = await client.post(
        "/api/v1/companies/",
        headers=headers,
        json={"name": name, "website": "https://acme.test"},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_skill(client, headers, name: str = "Python") -> dict:
    response = await client.post(
        "/api/v1/skills/",
        headers=headers,
        json={"name": name, "category": "LANGUAGE"},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_experience(
    client, headers, company_id: int, position: str = "Software Engineer"
) -> dict:
    response = await client.post(
        BASE + "/",
        headers=headers,
        json={
            "company_id": company_id,
            "position_title": position,
            "start_date": "2022-01-01",
            "end_date": None,
            "description": "Built things at this company.",
            "achievements": [],
            "skill_ids": [],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# POST /api/v1/experiences/
# ---------------------------------------------------------------------------


async def test_create_experience_returns_201_with_data(client, auth_headers):
    """Creating an experience returns 201 with full detail response."""
    company = await create_company(client, auth_headers)

    response = await client.post(
        BASE + "/",
        headers=auth_headers,
        json={
            "company_id": company["id"],
            "position_title": "Backend Developer",
            "start_date": "2021-03-01",
            "end_date": None,
            "description": "Developed REST APIs.",
            "achievements": [],
            "skill_ids": [],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["position_title"] == "Backend Developer"
    assert body["company_id"] == company["id"]
    assert body["start_date"] == "2021-03-01"
    assert "id" in body
    assert "user_id" in body


async def test_create_experience_with_achievements(client, auth_headers):
    """Creating an experience with inline achievements stores them."""
    company = await create_company(client, auth_headers)

    response = await client.post(
        BASE + "/",
        headers=auth_headers,
        json={
            "company_id": company["id"],
            "position_title": "Lead Engineer",
            "start_date": "2020-01-01",
            "end_date": "2023-01-01",
            "description": "Led the team.",
            "achievements": [
                {"title": "Shipped v2", "description": "Delivered major release."}
            ],
            "skill_ids": [],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert len(body.get("achievements", [])) == 1
    assert body["achievements"][0]["title"] == "Shipped v2"


async def test_create_experience_requires_auth(client):
    """POST /experiences/ without auth returns 401."""
    response = await client.post(BASE + "/", json={})
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/v1/experiences/
# ---------------------------------------------------------------------------


async def test_created_experience_appears_in_list(client, auth_headers):
    """An experience created via POST must appear in GET /experiences/."""
    company = await create_company(client, auth_headers)
    created = await create_experience(client, auth_headers, company["id"])

    response = await client.get(BASE + "/", headers=auth_headers)

    assert response.status_code == 200
    ids = [e["id"] for e in response.json()]
    assert created["id"] in ids


async def test_list_experiences_filter_by_company(client, auth_headers):
    """GET /experiences/?company_id=N returns only experiences for that company."""
    company_a = await create_company(client, auth_headers, name="Company A")
    company_b = await create_company(client, auth_headers, name="Company B")
    exp_a = await create_experience(client, auth_headers, company_a["id"])
    await create_experience(client, auth_headers, company_b["id"])

    response = await client.get(
        BASE + "/",
        headers=auth_headers,
        params={"company_id": company_a["id"]},
    )

    assert response.status_code == 200
    ids = [e["id"] for e in response.json()]
    assert exp_a["id"] in ids
    assert all(e["company_id"] == company_a["id"] for e in response.json())


# ---------------------------------------------------------------------------
# GET /api/v1/experiences/{id}
# ---------------------------------------------------------------------------


async def test_created_experience_retrievable_by_id(client, auth_headers):
    """An experience created via POST can be fetched by its ID."""
    company = await create_company(client, auth_headers)
    created = await create_experience(
        client, auth_headers, company["id"], position="DevOps Engineer"
    )

    response = await client.get(f"{BASE}/{created['id']}", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["position_title"] == "DevOps Engineer"


async def test_get_nonexistent_experience_returns_404(client, auth_headers):
    """GET /experiences/999999 returns 404."""
    response = await client.get(f"{BASE}/999999", headers=auth_headers)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/v1/experiences/{id}
# ---------------------------------------------------------------------------


async def test_update_experience_changes_values(client, auth_headers):
    """PUT /experiences/{id} updates position_title; GET by id reflects the change."""
    company = await create_company(client, auth_headers)
    created = await create_experience(
        client, auth_headers, company["id"], position="Old Title"
    )

    put = await client.put(
        f"{BASE}/{created['id']}",
        headers=auth_headers,
        json={"position_title": "New Title", "description": "Updated description."},
    )
    assert put.status_code == 200

    get = await client.get(f"{BASE}/{created['id']}", headers=auth_headers)
    assert get.json()["position_title"] == "New Title"


# ---------------------------------------------------------------------------
# DELETE /api/v1/experiences/{id}
# ---------------------------------------------------------------------------


async def test_delete_experience_soft_deletes(client, auth_headers):
    """DELETE /experiences/{id} soft-deletes; include_deleted shows deleted_at."""
    company = await create_company(client, auth_headers)
    created = await create_experience(client, auth_headers, company["id"])

    delete = await client.delete(f"{BASE}/{created['id']}", headers=auth_headers)
    assert delete.status_code == 200

    detail = await client.get(
        f"{BASE}/{created['id']}",
        headers=auth_headers,
        params={"include_deleted": "true"},
    )
    assert detail.status_code == 200
    assert detail.json()["deleted_at"] is not None


async def test_deleted_experience_excluded_from_list(client, auth_headers):
    """Soft-deleted experiences do not appear in the default list."""
    company = await create_company(client, auth_headers)
    created = await create_experience(client, auth_headers, company["id"])

    await client.delete(f"{BASE}/{created['id']}", headers=auth_headers)

    list_response = await client.get(BASE + "/", headers=auth_headers)
    ids = [e["id"] for e in list_response.json()]
    assert created["id"] not in ids


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------


async def test_add_achievement_to_experience(client, auth_headers):
    """POST /experiences/{id}/achievements returns 201 with achievement data."""
    company = await create_company(client, auth_headers)
    exp = await create_experience(client, auth_headers, company["id"])

    response = await client.post(
        f"{BASE}/{exp['id']}/achievements",
        headers=auth_headers,
        json={"title": "Launched Feature X", "description": "Delivered major feature."},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Launched Feature X"
    assert body["experience_id"] == exp["id"]
    assert "id" in body


async def test_achievement_appears_in_experience_detail(client, auth_headers):
    """An added achievement should appear in GET /experiences/{id}."""
    company = await create_company(client, auth_headers)
    exp = await create_experience(client, auth_headers, company["id"])

    await client.post(
        f"{BASE}/{exp['id']}/achievements",
        headers=auth_headers,
        json={"title": "Visible Achievement", "description": "Must appear."},
    )

    detail = await client.get(f"{BASE}/{exp['id']}", headers=auth_headers)
    assert detail.status_code == 200
    achievements = detail.json().get("achievements", [])
    titles = [a["title"] for a in achievements]
    assert "Visible Achievement" in titles


async def test_update_achievement(client, auth_headers):
    """PUT /experiences/achievements/{id} updates the achievement."""
    company = await create_company(client, auth_headers)
    exp = await create_experience(client, auth_headers, company["id"])

    add = await client.post(
        f"{BASE}/{exp['id']}/achievements",
        headers=auth_headers,
        json={"title": "Old Title", "description": "Old desc."},
    )
    achievement_id = add.json()["id"]

    update = await client.put(
        f"{BASE}/achievements/{achievement_id}",
        headers=auth_headers,
        json={"title": "Updated Title", "description": "New desc."},
    )

    assert update.status_code == 200
    assert update.json()["title"] == "Updated Title"


async def test_remove_achievement_returns_204(client, auth_headers):
    """DELETE /experiences/achievements/{id} returns 204."""
    company = await create_company(client, auth_headers)
    exp = await create_experience(client, auth_headers, company["id"])

    add = await client.post(
        f"{BASE}/{exp['id']}/achievements",
        headers=auth_headers,
        json={"title": "To Remove", "description": "Will be deleted."},
    )
    achievement_id = add.json()["id"]

    delete = await client.delete(
        f"{BASE}/achievements/{achievement_id}",
        headers=auth_headers,
    )
    assert delete.status_code == 204


# ---------------------------------------------------------------------------
# Skill associations
# ---------------------------------------------------------------------------


async def test_add_skill_to_experience_returns_201(client, auth_headers):
    """POST /experiences/{id}/skills/{skill_id} returns 201."""
    company = await create_company(client, auth_headers)
    exp = await create_experience(client, auth_headers, company["id"])
    skill = await create_skill(client, auth_headers, name="Docker")

    response = await client.post(
        f"{BASE}/{exp['id']}/skills/{skill['id']}",
        headers=auth_headers,
    )
    assert response.status_code == 201


async def test_remove_skill_from_experience_returns_204(client, auth_headers):
    """DELETE /experiences/{id}/skills/{skill_id} returns 204."""
    company = await create_company(client, auth_headers)
    exp = await create_experience(client, auth_headers, company["id"])
    skill = await create_skill(client, auth_headers, name="Kubernetes")

    await client.post(f"{BASE}/{exp['id']}/skills/{skill['id']}", headers=auth_headers)

    delete = await client.delete(
        f"{BASE}/{exp['id']}/skills/{skill['id']}",
        headers=auth_headers,
    )
    assert delete.status_code == 204
