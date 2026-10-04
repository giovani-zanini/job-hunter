"""E2E tests for /api/v1/links/ endpoints.

Covered:
    POST   /api/v1/links/        – create link
    GET    /api/v1/links/        – list links (+ filters)
    GET    /api/v1/links/{id}    – get link by ID
    PUT    /api/v1/links/{id}    – update link
    DELETE /api/v1/links/{id}    – soft-delete link

Note: The ``from`` JSON key is a Python reserved keyword, so the Pydantic
DTO uses ``from_`` with ``alias="from"``. Requests must use ``"from"`` as
the key; responses also expose ``"from"``.
"""

import pytest


pytestmark = pytest.mark.asyncio

BASE = "/api/v1/links"


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


async def create_link(
    client,
    type_: str = "SOCIAL_MEDIA",
    from_: str = "linkedin",
    value: str = "https://linkedin.com/in/testuser",
) -> dict:
    response = await client.post(
        BASE + "/",
        json={"type": type_, "from": from_, "value": value},
    )
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# POST /api/v1/links/
# ---------------------------------------------------------------------------


async def test_create_link_returns_201_with_data(client):
    """Creating a link returns 201 with id, type, from and value."""
    response = await client.post(
        BASE + "/",
        json={
            "type": "SOCIAL_MEDIA",
            "from": "github",
            "value": "https://github.com/test",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "SOCIAL_MEDIA"
    assert body["from"] == "github"
    assert body["value"] == "https://github.com/test"
    assert "id" in body
    assert "user_id" in body




async def test_create_link_invalid_type_returns_422(client):
    """An invalid link type returns 422."""
    response = await client.post(
        BASE + "/",
        json={"type": "INVALID_TYPE", "from": "github", "value": "https://github.com"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/links/
# ---------------------------------------------------------------------------


async def test_created_link_appears_in_list(client):
    """A link created via POST must appear in GET /links/."""
    created = await create_link(
        client, from_="twitter", value="https://twitter.com/test"
    )

    response = await client.get(BASE + "/")

    assert response.status_code == 200
    ids = [lnk["id"] for lnk in response.json()]
    assert created["id"] in ids


async def test_list_links_filter_by_type(client):
    """GET /links/?type=EMAIL returns only EMAIL links."""
    await create_link(
        client, type_="EMAIL", from_="gmail", value="me@gmail.com"
    )
    await create_link(
        client,
        type_="SOCIAL_MEDIA",
        from_="linkedin",
        value="https://linkedin.com/in/a",
    )

    response = await client.get(
        BASE + "/", params={"type": "EMAIL"}
    )

    assert response.status_code == 200
    items = response.json()
    assert all(lnk["type"] == "EMAIL" for lnk in items)


async def test_list_links_empty_initially(client):
    """GET /links/ returns an empty list when no links exist."""
    response = await client.get(BASE + "/")
    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# GET /api/v1/links/{id}
# ---------------------------------------------------------------------------


async def test_created_link_retrievable_by_id(client):
    """A link created via POST can be fetched by its ID."""
    created = await create_link(
        client, type_="CELLPHONE", from_="mobile", value="+5511999999999"
    )

    response = await client.get(f"{BASE}/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["type"] == "CELLPHONE"
    assert body["from"] == "mobile"


async def test_get_nonexistent_link_returns_404(client):
    """GET /links/999999 returns 404."""
    response = await client.get(f"{BASE}/999999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/v1/links/{id}
# ---------------------------------------------------------------------------


async def test_update_link_changes_values(client):
    """PUT /links/{id} updates the value; GET by id reflects the change."""
    created = await create_link(
        client, from_="old_platform", value="https://old.example.com"
    )

    put_response = await client.put(
        f"{BASE}/{created['id']}",
        json={"from": "new_platform", "value": "https://new.example.com"},
    )
    assert put_response.status_code == 200

    get_response = await client.get(f"{BASE}/{created['id']}")
    body = get_response.json()
    assert body["from"] == "new_platform"
    assert body["value"] == "https://new.example.com"


# ---------------------------------------------------------------------------
# DELETE /api/v1/links/{id}
# ---------------------------------------------------------------------------


async def test_delete_link_soft_deletes(client):
    """DELETE /links/{id} soft-deletes; detail with include_deleted shows deleted_at."""
    created = await create_link(
        client, from_="to_delete", value="https://delete.example.com"
    )

    delete = await client.delete(f"{BASE}/{created['id']}")
    assert delete.status_code == 200

    detail = await client.get(
        f"{BASE}/{created['id']}",
        params={"include_deleted": "true"},
    )
    assert detail.status_code == 200
    assert detail.json()["deleted_at"] is not None


async def test_deleted_link_excluded_from_list(client):
    """Soft-deleted links do not appear in the default list."""
    created = await create_link(
        client, from_="gone", value="https://gone.example.com"
    )

    await client.delete(f"{BASE}/{created['id']}")

    list_response = await client.get(BASE + "/")
    ids = [lnk["id"] for lnk in list_response.json()]
    assert created["id"] not in ids
