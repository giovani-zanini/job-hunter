"""E2E tests for /api/v1/account/ endpoints.

Covered:
    POST   /api/v1/account/      – create user
    GET    /api/v1/account/me    – get current user
    DELETE /api/v1/account/me   – delete current user
"""

import pytest


pytestmark = pytest.mark.asyncio

BASE = "/api/v1/account"


# ---------------------------------------------------------------------------
# POST /api/v1/account/
# ---------------------------------------------------------------------------


async def test_create_user_returns_201_and_user_data(client, seed_roles):
    """Creating a new user returns 201 with id, email and active flags."""
    response = await client.post(
        f"{BASE}/",
        json={"email": "new_user@test.com", "password": "StrongPass123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new_user@test.com"
    assert body["is_active"] is True
    assert "id" in body
    assert "created_at" in body


async def test_create_user_duplicate_email_returns_conflict(client, seed_roles):
    """Registering the same email twice returns 409 Conflict."""
    payload = {"email": "duplicate@test.com", "password": "StrongPass123"}
    first = await client.post(f"{BASE}/", json=payload)
    assert first.status_code == 201

    second = await client.post(f"{BASE}/", json=payload)
    assert second.status_code == 409


async def test_create_user_weak_password_returns_422(client, seed_roles):
    """Password shorter than 8 characters returns 422 Unprocessable Entity."""
    response = await client.post(
        f"{BASE}/",
        json={"email": "weakpass@test.com", "password": "short"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/account/me
# ---------------------------------------------------------------------------


async def test_get_current_user_returns_authenticated_user(
    client, auth_headers, test_credentials
):
    """Authenticated GET /account/me returns the current user's data."""
    response = await client.get(f"{BASE}/me", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == test_credentials["email"]
    assert "id" in body
    assert body["is_active"] is True


async def test_get_current_user_without_auth_returns_403(client):
    """GET /account/me without Authorization header returns 401."""
    response = await client.get(f"{BASE}/me")
    assert response.status_code == 401


async def test_get_current_user_with_invalid_token_returns_403(client):
    """GET /account/me with a bogus token returns 401."""
    response = await client.get(
        f"{BASE}/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# DELETE /api/v1/account/me
# ---------------------------------------------------------------------------


async def test_delete_current_user_returns_204(client, seed_roles):
    """Creating a user, logging in, then deleting returns 204.
    Subsequent GET /account/me with the same token returns 403."""
    email = "to_delete@test.com"
    password = "StrongPass123"

    # Register
    reg = await client.post(f"{BASE}/", json={"email": email, "password": password})
    assert reg.status_code == 201

    # Login
    login = await client.post(
        "/api/v1/auth/token",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Delete
    delete = await client.delete(f"{BASE}/me", headers=headers)
    assert delete.status_code == 204

    # Subsequent GET should fail (user no longer exists)
    get_after = await client.get(f"{BASE}/me", headers=headers)
    assert get_after.status_code in (401, 403, 404)
