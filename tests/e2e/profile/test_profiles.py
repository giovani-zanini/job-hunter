"""E2E tests for /api/v1/profiles/ endpoints.

Covered (CRUD):
    POST   /api/v1/profiles/              – create profile
    GET    /api/v1/profiles/              – list profiles
    GET    /api/v1/profiles/{id}          – get profile by ID
    PUT    /api/v1/profiles/{id}          – update profile
    DELETE /api/v1/profiles/{id}          – soft-delete profile

Covered (Skill associations):
    POST   /api/v1/profiles/{id}/skills              – add skill to profile
    PUT    /api/v1/profiles/{id}/skills/{skill_id}   – update profile skill
    DELETE /api/v1/profiles/{id}/skills/{skill_id}   – remove skill from profile

Covered (other associations):
    POST   /api/v1/profiles/{id}/links/{link_id}                  – add link
    DELETE /api/v1/profiles/{id}/links/{link_id}                  – remove link
    POST   /api/v1/profiles/{id}/experiences/{experience_id}      – add experience
    DELETE /api/v1/profiles/{id}/experiences/{experience_id}      – remove experience
    POST   /api/v1/profiles/{id}/education/{education_id}         – add education
    DELETE /api/v1/profiles/{id}/education/{education_id}         – remove education
    POST   /api/v1/profiles/{id}/certificates/{certificate_id}    – add certificate
    DELETE /api/v1/profiles/{id}/certificates/{certificate_id}    – remove certificate
"""

import pytest


pytestmark = pytest.mark.asyncio

BASE = "/api/v1/profiles"


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


async def create_profile(
    client,
    slug: str = "test-profile",
    full_name: str = "Test User",
    title: str = "Software Engineer",
    bio: str = "E2E test profile bio.",
) -> dict:
    response = await client.post(
        BASE + "/",
        json={"slug": slug, "full_name": full_name, "title": title, "bio": bio},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_skill(
    client, name: str = "Python", category: str = "LANGUAGE"
) -> dict:
    response = await client.post(
        "/api/v1/skills/",
        json={"name": name, "category": category},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_company(client, name: str = "Acme Corp") -> dict:
    response = await client.post(
        "/api/v1/companies/",
        json={"name": name, "website": "https://acme.test"},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_link(client) -> dict:
    response = await client.post(
        "/api/v1/links/",
        json={
            "type": "SOCIAL_MEDIA",
            "from": "linkedin",
            "value": "https://linkedin.com/in/test",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_experience(client, company_id: int) -> dict:
    response = await client.post(
        "/api/v1/experiences/",
        json={
            "company_id": company_id,
            "position_title": "Software Engineer",
            "start_date": "2022-01-01",
            "end_date": None,
            "description": "Built amazing things.",
            "achievements": [],
            "skill_ids": [],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_education(client) -> dict:
    response = await client.post(
        "/api/v1/education/",
        json={
            "institution_name": "MIT",
            "degree": "Bachelor",
            "field_of_study": "Computer Science",
            "start_date": "2019-01-01",
            "end_date": "2023-01-01",
            "skill_ids": [],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_certificate(client) -> dict:
    response = await client.post(
        "/api/v1/certificates/",
        json={
            "name": "AWS Solutions Architect",
            "issuer": "Amazon",
            "issue_date": "2024-01-01",
            "expiration_date": None,
            "credential_url": None,
            "skill_ids": [],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# POST /api/v1/profiles/
# ---------------------------------------------------------------------------


async def test_create_profile_returns_201_with_data(client):
    """Creating a profile returns 201 with id, user_id, slug, full_name, title, bio."""
    response = await client.post(
        BASE + "/",
        json={
            "slug": "my-profile",
            "full_name": "Jane Doe",
            "title": "Backend Engineer",
            "bio": "Building APIs.",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["slug"] == "my-profile"
    assert body["full_name"] == "Jane Doe"
    assert body["title"] == "Backend Engineer"
    assert "id" in body
    assert "user_id" in body




async def test_create_profile_duplicate_slug_returns_conflict(client):
    """Creating two profiles with the same slug returns 409 Conflict."""
    await create_profile(client, slug="unique-slug")
    response = await client.post(
        BASE + "/",
        json={
            "slug": "unique-slug",
            "full_name": "Other",
            "title": "Other",
            "bio": "Other",
        },
    )
    assert response.status_code == 409


# ---------------------------------------------------------------------------
# GET /api/v1/profiles/
# ---------------------------------------------------------------------------


async def test_created_profile_appears_in_list(client):
    """A profile created via POST must appear in GET /profiles/."""
    created = await create_profile(client, slug="list-me")

    response = await client.get(BASE + "/")

    assert response.status_code == 200
    ids = [p["id"] for p in response.json()]
    assert created["id"] in ids


async def test_list_profiles_filter_by_slug(client):
    """GET /profiles/?slug=partial returns only matching profiles."""
    await create_profile(client, slug="engineer-profile")
    await create_profile(client, slug="designer-profile")

    response = await client.get(
        BASE + "/", params={"slug": "engineer"}
    )

    assert response.status_code == 200
    slugs = [p["slug"] for p in response.json()]
    assert "engineer-profile" in slugs
    assert "designer-profile" not in slugs


# ---------------------------------------------------------------------------
# GET /api/v1/profiles/{id}
# ---------------------------------------------------------------------------


async def test_created_profile_retrievable_by_id(client):
    """A profile created via POST can be fetched by its ID."""
    created = await create_profile(
        client, slug="get-by-id", full_name="Retrieve Me"
    )

    response = await client.get(f"{BASE}/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["full_name"] == "Retrieve Me"


async def test_get_nonexistent_profile_returns_404(client):
    """GET /profiles/999999 returns 404."""
    response = await client.get(f"{BASE}/999999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/v1/profiles/{id}
# ---------------------------------------------------------------------------


async def test_update_profile_changes_values(client):
    """PUT /profiles/{id} updates fields; GET by id reflects the changes."""
    created = await create_profile(
        client, slug="to-update", full_name="Before Update"
    )

    put = await client.put(
        f"{BASE}/{created['id']}",
        json={"full_name": "After Update", "title": "Updated Title"},
    )
    assert put.status_code == 200

    get = await client.get(f"{BASE}/{created['id']}")
    body = get.json()
    assert body["full_name"] == "After Update"
    assert body["title"] == "Updated Title"


# ---------------------------------------------------------------------------
# DELETE /api/v1/profiles/{id}
# ---------------------------------------------------------------------------


async def test_delete_profile_soft_deletes(client):
    """DELETE /profiles/{id} soft-deletes the profile."""
    created = await create_profile(client, slug="to-delete-profile")

    delete = await client.delete(f"{BASE}/{created['id']}")
    assert delete.status_code == 200

    # The profile should no longer appear in the default list
    list_response = await client.get(BASE + "/")
    ids = [p["id"] for p in list_response.json()]
    assert created["id"] not in ids


# ---------------------------------------------------------------------------
# Skill associations
# ---------------------------------------------------------------------------


async def test_add_skill_to_profile_returns_201(client):
    """POST /profiles/{id}/skills returns 201 with the association data."""
    profile = await create_profile(client, slug="skill-profile")
    skill = await create_skill(client, name="Python")

    response = await client.post(
        f"{BASE}/{profile['id']}/skills",
        json={
            "skill_id": skill["id"],
            "level": 4,
            "years_of_experience": 3,
            "last_used_at": None,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["skill_id"] == skill["id"]
    assert body["level"] == 4
    assert body["years_of_experience"] == 3


async def test_update_profile_skill_changes_level(client):
    """PUT /profiles/{id}/skills/{skill_id} updates level and years."""
    profile = await create_profile(client, slug="update-skill-profile")
    skill = await create_skill(client, name="Go")

    await client.post(
        f"{BASE}/{profile['id']}/skills",
        json={
            "skill_id": skill["id"],
            "level": 2,
            "years_of_experience": 1,
            "last_used_at": None,
        },
    )

    update = await client.put(
        f"{BASE}/{profile['id']}/skills/{skill['id']}",
        json={"level": 5, "years_of_experience": 4},
    )
    assert update.status_code == 200
    body = update.json()
    assert body["level"] == 5
    assert body["years_of_experience"] == 4


async def test_remove_skill_from_profile_returns_204(client):
    """DELETE /profiles/{id}/skills/{skill_id} returns 204."""
    profile = await create_profile(client, slug="remove-skill-profile")
    skill = await create_skill(client, name="Rust")

    await client.post(
        f"{BASE}/{profile['id']}/skills",
        json={
            "skill_id": skill["id"],
            "level": 3,
            "years_of_experience": 2,
            "last_used_at": None,
        },
    )

    delete = await client.delete(
        f"{BASE}/{profile['id']}/skills/{skill['id']}",

    )
    assert delete.status_code == 204


# ---------------------------------------------------------------------------
# Link associations
# ---------------------------------------------------------------------------


async def test_add_link_to_profile_returns_201(client):
    """POST /profiles/{id}/links/{link_id} returns 201."""
    profile = await create_profile(client, slug="link-profile")
    link = await create_link(client)

    response = await client.post(
        f"{BASE}/{profile['id']}/links/{link['id']}",

    )
    assert response.status_code == 201


async def test_remove_link_from_profile_returns_204(client):
    """DELETE /profiles/{id}/links/{link_id} returns 204."""
    profile = await create_profile(client, slug="remove-link-profile")
    link = await create_link(client)

    await client.post(
        f"{BASE}/{profile['id']}/links/{link['id']}"
    )

    delete = await client.delete(
        f"{BASE}/{profile['id']}/links/{link['id']}",

    )
    assert delete.status_code == 204


# ---------------------------------------------------------------------------
# Experience associations
# ---------------------------------------------------------------------------


async def test_add_experience_to_profile_returns_201(client):
    """POST /profiles/{id}/experiences/{experience_id} returns 201."""
    profile = await create_profile(client, slug="exp-profile")
    company = await create_company(client)
    experience = await create_experience(client, company_id=company["id"])

    response = await client.post(
        f"{BASE}/{profile['id']}/experiences/{experience['id']}",

    )
    assert response.status_code == 201


async def test_remove_experience_from_profile_returns_204(client):
    """DELETE /profiles/{id}/experiences/{experience_id} returns 204."""
    profile = await create_profile(client, slug="remove-exp-profile")
    company = await create_company(client)
    experience = await create_experience(client, company_id=company["id"])

    await client.post(
        f"{BASE}/{profile['id']}/experiences/{experience['id']}",

    )

    delete = await client.delete(
        f"{BASE}/{profile['id']}/experiences/{experience['id']}",

    )
    assert delete.status_code == 204


# ---------------------------------------------------------------------------
# Education associations
# ---------------------------------------------------------------------------


async def test_add_education_to_profile_returns_201(client):
    """POST /profiles/{id}/education/{education_id} returns 201."""
    profile = await create_profile(client, slug="edu-profile")
    education = await create_education(client)

    response = await client.post(
        f"{BASE}/{profile['id']}/education/{education['id']}",

    )
    assert response.status_code == 201


async def test_remove_education_from_profile_returns_204(client):
    """DELETE /profiles/{id}/education/{education_id} returns 204."""
    profile = await create_profile(client, slug="remove-edu-profile")
    education = await create_education(client)

    await client.post(
        f"{BASE}/{profile['id']}/education/{education['id']}",

    )

    delete = await client.delete(
        f"{BASE}/{profile['id']}/education/{education['id']}",

    )
    assert delete.status_code == 204


# ---------------------------------------------------------------------------
# Certificate associations
# ---------------------------------------------------------------------------


async def test_add_certificate_to_profile_returns_201(client):
    """POST /profiles/{id}/certificates/{certificate_id} returns 201."""
    profile = await create_profile(client, slug="cert-profile")
    certificate = await create_certificate(client)

    response = await client.post(
        f"{BASE}/{profile['id']}/certificates/{certificate['id']}",

    )
    assert response.status_code == 201


async def test_remove_certificate_from_profile_returns_204(client):
    """DELETE /profiles/{id}/certificates/{certificate_id} returns 204."""
    profile = await create_profile(client, slug="remove-cert-profile")
    certificate = await create_certificate(client)

    await client.post(
        f"{BASE}/{profile['id']}/certificates/{certificate['id']}",

    )

    delete = await client.delete(
        f"{BASE}/{profile['id']}/certificates/{certificate['id']}",

    )
    assert delete.status_code == 204
