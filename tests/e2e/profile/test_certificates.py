"""E2E tests for /api/v1/certificates/ endpoints.

Covered (CRUD):
    POST   /api/v1/certificates/        – create certificate
    GET    /api/v1/certificates/        – list certificates
    GET    /api/v1/certificates/{id}    – get by ID
    PUT    /api/v1/certificates/{id}    – update
    DELETE /api/v1/certificates/{id}    – soft-delete

Covered (Skills):
    POST   /api/v1/certificates/{id}/skills/{skill_id}   – add skill
    DELETE /api/v1/certificates/{id}/skills/{skill_id}   – remove skill
"""

import pytest


pytestmark = pytest.mark.asyncio

BASE = "/api/v1/certificates"


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


async def create_certificate(
    client,
    headers,
    name: str = "AWS Solutions Architect",
    issuer: str = "Amazon Web Services",
    issue_date: str = "2024-01-15",
) -> dict:
    response = await client.post(
        BASE + "/",
        headers=headers,
        json={
            "name": name,
            "issuer": issuer,
            "issue_date": issue_date,
            "expiration_date": None,
            "credential_url": None,
            "skill_ids": [],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_skill(client, headers, name: str = "Python") -> dict:
    response = await client.post(
        "/api/v1/skills/",
        headers=headers,
        json={"name": name, "category": "TOOL"},
    )
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# POST /api/v1/certificates/
# ---------------------------------------------------------------------------


async def test_create_certificate_returns_201_with_data(client, auth_headers):
    """Creating a certificate returns 201 with all expected fields."""
    response = await client.post(
        BASE + "/",
        headers=auth_headers,
        json={
            "name": "Google Professional Cloud Architect",
            "issuer": "Google",
            "issue_date": "2023-06-01",
            "expiration_date": "2025-06-01",
            "credential_url": "https://google.com/cert/123",
            "skill_ids": [],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Google Professional Cloud Architect"
    assert body["issuer"] == "Google"
    assert body["issue_date"] == "2023-06-01"
    assert body["expiration_date"] == "2025-06-01"
    assert body["credential_url"] == "https://google.com/cert/123"
    assert "id" in body
    assert "user_id" in body


async def test_create_certificate_requires_auth(client):
    """POST /certificates/ without auth returns 401."""
    response = await client.post(BASE + "/", json={})
    assert response.status_code == 401


async def test_create_certificate_missing_fields_returns_422(client, auth_headers):
    """Missing required fields returns 422."""
    response = await client.post(
        BASE + "/",
        headers=auth_headers,
        json={"name": "Incomplete"},
    )
    assert response.status_code == 422


async def test_create_certificate_with_optional_fields_null(client, auth_headers):
    """Certificate with null optional fields returns 201."""
    response = await client.post(
        BASE + "/",
        headers=auth_headers,
        json={
            "name": "Minimal Cert",
            "issuer": "SomeOrg",
            "issue_date": "2024-01-01",
            "expiration_date": None,
            "credential_url": None,
            "skill_ids": [],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["expiration_date"] is None
    assert body["credential_url"] is None


# ---------------------------------------------------------------------------
# GET /api/v1/certificates/
# ---------------------------------------------------------------------------


async def test_created_certificate_appears_in_list(client, auth_headers):
    """A certificate created via POST must appear in GET /certificates/."""
    created = await create_certificate(client, auth_headers, name="List This Cert")

    response = await client.get(BASE + "/", headers=auth_headers)

    assert response.status_code == 200
    ids = [c["id"] for c in response.json()]
    assert created["id"] in ids


async def test_list_certificates_filter_by_name(client, auth_headers):
    """GET /certificates/?name=partial returns only matching certificates."""
    await create_certificate(client, auth_headers, name="Azure Fundamentals")
    await create_certificate(client, auth_headers, name="AWS Cloud Practitioner")

    response = await client.get(
        BASE + "/", headers=auth_headers, params={"name": "Azure"}
    )

    assert response.status_code == 200
    items = response.json()
    assert any(c["name"] == "Azure Fundamentals" for c in items)
    assert all("Azure" in c["name"] for c in items)


async def test_list_certificates_filter_by_issuer(client, auth_headers):
    """GET /certificates/?issuer=partial returns only matching certificates."""
    await create_certificate(client, auth_headers, name="Cert A", issuer="Microsoft")
    await create_certificate(client, auth_headers, name="Cert B", issuer="Google")

    response = await client.get(
        BASE + "/", headers=auth_headers, params={"issuer": "Microsoft"}
    )

    assert response.status_code == 200
    items = response.json()
    assert all("Microsoft" in c["issuer"] for c in items)


async def test_list_certificates_empty_initially(client, auth_headers):
    """GET /certificates/ returns an empty list when none exist."""
    response = await client.get(BASE + "/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# GET /api/v1/certificates/{id}
# ---------------------------------------------------------------------------


async def test_created_certificate_retrievable_by_id(client, auth_headers):
    """A certificate created via POST can be fetched by its ID."""
    created = await create_certificate(client, auth_headers, name="Fetch By ID Cert")

    response = await client.get(f"{BASE}/{created['id']}", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["name"] == "Fetch By ID Cert"


async def test_get_nonexistent_certificate_returns_404(client, auth_headers):
    """GET /certificates/999999 returns 404."""
    response = await client.get(f"{BASE}/999999", headers=auth_headers)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/v1/certificates/{id}
# ---------------------------------------------------------------------------


async def test_update_certificate_changes_values(client, auth_headers):
    """PUT /certificates/{id} updates name and issuer; GET by id reflects changes."""
    created = await create_certificate(client, auth_headers, name="OldCertName")

    put = await client.put(
        f"{BASE}/{created['id']}",
        headers=auth_headers,
        json={"name": "NewCertName", "issuer": "UpdatedOrg"},
    )
    assert put.status_code == 200

    get = await client.get(f"{BASE}/{created['id']}", headers=auth_headers)
    body = get.json()
    assert body["name"] == "NewCertName"
    assert body["issuer"] == "UpdatedOrg"


# ---------------------------------------------------------------------------
# DELETE /api/v1/certificates/{id}
# ---------------------------------------------------------------------------


async def test_delete_certificate_soft_deletes(client, auth_headers):
    """DELETE /certificates/{id} soft-deletes; detail with include_deleted shows deleted_at."""
    created = await create_certificate(client, auth_headers, name="Delete Me Cert")

    delete = await client.delete(f"{BASE}/{created['id']}", headers=auth_headers)
    assert delete.status_code == 200

    detail = await client.get(
        f"{BASE}/{created['id']}",
        headers=auth_headers,
        params={"include_deleted": "true"},
    )
    assert detail.status_code == 200
    assert detail.json()["deleted_at"] is not None


async def test_deleted_certificate_excluded_from_list(client, auth_headers):
    """Soft-deleted certificates do not appear in the default list."""
    created = await create_certificate(client, auth_headers, name="Gone Cert")

    await client.delete(f"{BASE}/{created['id']}", headers=auth_headers)

    list_response = await client.get(BASE + "/", headers=auth_headers)
    ids = [c["id"] for c in list_response.json()]
    assert created["id"] not in ids


# ---------------------------------------------------------------------------
# Skill associations
# ---------------------------------------------------------------------------


async def test_add_skill_to_certificate_returns_201(client, auth_headers):
    """POST /certificates/{id}/skills/{skill_id} returns 201."""
    cert = await create_certificate(client, auth_headers, name="Skill Cert")
    skill = await create_skill(client, auth_headers, name="Terraform")

    response = await client.post(
        f"{BASE}/{cert['id']}/skills/{skill['id']}",
        headers=auth_headers,
    )
    assert response.status_code == 201


async def test_remove_skill_from_certificate_returns_204(client, auth_headers):
    """DELETE /certificates/{id}/skills/{skill_id} returns 204."""
    cert = await create_certificate(client, auth_headers, name="Remove Skill Cert")
    skill = await create_skill(client, auth_headers, name="Ansible")

    await client.post(
        f"{BASE}/{cert['id']}/skills/{skill['id']}",
        headers=auth_headers,
    )

    delete = await client.delete(
        f"{BASE}/{cert['id']}/skills/{skill['id']}",
        headers=auth_headers,
    )
    assert delete.status_code == 204
