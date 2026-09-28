"""E2E tests for /api/v1/companies/ endpoints.

Covered:
    POST   /api/v1/companies/         – create company
    GET    /api/v1/companies/         – list companies (+ filters)
    GET    /api/v1/companies/{id}     – get company by ID
    PUT    /api/v1/companies/{id}     – update company
    DELETE /api/v1/companies/{id}     – soft-delete company
"""

import pytest


pytestmark = pytest.mark.asyncio

BASE = "/api/v1/companies"


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


async def create_company(
    client, headers, name="Acme Corp", website="https://acme.example.com"
) -> dict:
    response = await client.post(
        BASE + "/",
        headers=headers,
        json={"name": name, "website": website},
    )
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# POST /api/v1/companies/
# ---------------------------------------------------------------------------


async def test_create_company_returns_201_with_data(client, auth_headers):
    """Creating a company returns 201 with id, name and website."""
    response = await client.post(
        BASE + "/",
        headers=auth_headers,
        json={"name": "TechCorp", "website": "https://techcorp.test"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "TechCorp"
    assert body["website"] == "https://techcorp.test"
    assert "id" in body


async def test_create_company_requires_auth(client):
    """POST /companies/ without auth returns 401."""
    response = await client.post(
        BASE + "/",
        json={"name": "Ghost Inc", "website": "https://ghost.test"},
    )
    assert response.status_code == 401


async def test_create_company_missing_fields_returns_422(client, auth_headers):
    """Missing required fields returns 422."""
    response = await client.post(
        BASE + "/", headers=auth_headers, json={"name": "Incomplete"}
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/companies/
# ---------------------------------------------------------------------------


async def test_created_company_appears_in_list(client, auth_headers):
    """A company created via POST must appear in GET /companies/."""
    created = await create_company(client, auth_headers, name="ListMe Inc")

    response = await client.get(BASE + "/", headers=auth_headers)

    assert response.status_code == 200
    ids = [c["id"] for c in response.json()]
    assert created["id"] in ids


async def test_list_companies_filter_by_name(client, auth_headers):
    """GET /companies/?name=partial returns only name-matching companies."""
    await create_company(client, auth_headers, name="Alpha Solutions")
    await create_company(client, auth_headers, name="Beta Labs")

    response = await client.get(
        BASE + "/", headers=auth_headers, params={"name": "Alpha"}
    )

    assert response.status_code == 200
    items = response.json()
    assert any(c["name"] == "Alpha Solutions" for c in items)
    assert all("Alpha" in c["name"] for c in items)


async def test_list_companies_empty_initially(client, auth_headers):
    """GET /companies/ returns an empty list when none exist."""
    response = await client.get(BASE + "/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# GET /api/v1/companies/{id}
# ---------------------------------------------------------------------------


async def test_created_company_retrievable_by_id(client, auth_headers):
    """A company created via POST can be fetched by its ID."""
    created = await create_company(client, auth_headers, name="GetMe Corp")

    response = await client.get(f"{BASE}/{created['id']}", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["name"] == "GetMe Corp"


async def test_get_nonexistent_company_returns_404(client, auth_headers):
    """GET /companies/999999 returns 404 Not Found."""
    response = await client.get(f"{BASE}/999999", headers=auth_headers)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/v1/companies/{id}
# ---------------------------------------------------------------------------


async def test_update_company_changes_values(client, auth_headers):
    """PUT /companies/{id} updates name; GET by id reflects the change."""
    created = await create_company(client, auth_headers, name="OldName LLC")

    put_response = await client.put(
        f"{BASE}/{created['id']}",
        headers=auth_headers,
        json={"name": "NewName LLC", "website": "https://newname.test"},
    )
    assert put_response.status_code == 200

    get_response = await client.get(f"{BASE}/{created['id']}", headers=auth_headers)
    assert get_response.json()["name"] == "NewName LLC"
    assert get_response.json()["website"] == "https://newname.test"


# ---------------------------------------------------------------------------
# DELETE /api/v1/companies/{id}
# ---------------------------------------------------------------------------


async def test_delete_company_soft_deletes(client, auth_headers):
    """DELETE /companies/{id} soft-deletes; detail with include_deleted shows deleted_at."""
    created = await create_company(client, auth_headers, name="DeleteMe Inc")

    delete = await client.delete(f"{BASE}/{created['id']}", headers=auth_headers)
    assert delete.status_code == 200

    detail = await client.get(
        f"{BASE}/{created['id']}",
        headers=auth_headers,
        params={"include_deleted": "true"},
    )
    assert detail.status_code == 200
    assert detail.json()["deleted_at"] is not None


async def test_deleted_company_excluded_from_list(client, auth_headers):
    """Soft-deleted companies do not appear in the default list."""
    created = await create_company(client, auth_headers, name="GoneCompany")

    await client.delete(f"{BASE}/{created['id']}", headers=auth_headers)

    list_response = await client.get(BASE + "/", headers=auth_headers)
    ids = [c["id"] for c in list_response.json()]
    assert created["id"] not in ids
