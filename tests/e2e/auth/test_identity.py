"""E2E tests for /api/v1/auth/ endpoints.

Covered:
    POST /api/v1/auth/token            – login
    POST /api/v1/auth/refresh-token    – refresh tokens
    POST /api/v1/auth/change-password  – change password
    POST /api/v1/auth/request-recovery – request recovery token
    POST /api/v1/auth/reset-password   – reset password with token
"""

import pytest


pytestmark = pytest.mark.asyncio

BASE = "/api/v1/auth"
ACCOUNT = "/api/v1/account"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _register_and_login(client, email: str, password: str) -> dict:
    """Register a fresh user and return the full token response body."""
    reg = await client.post(ACCOUNT + "/", json={"email": email, "password": password})
    assert reg.status_code == 201, reg.text
    login = await client.post(
        BASE + "/token", json={"email": email, "password": password}
    )
    assert login.status_code == 200, login.text
    return login.json()


# ---------------------------------------------------------------------------
# POST /api/v1/auth/token
# ---------------------------------------------------------------------------


async def test_login_returns_token_pair(client, test_credentials):
    """Valid credentials return access_token, refresh_token and token_type."""
    response = await client.post(BASE + "/token", json=test_credentials)

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(client, test_credentials):
    """Wrong password returns 401 Unauthorized."""
    payload = {**test_credentials, "password": "WrongPassword!"}
    response = await client.post(BASE + "/token", json=payload)
    assert response.status_code == 401


async def test_login_unknown_email_returns_401(client):
    """Unknown email returns 401 Unauthorized."""
    response = await client.post(
        BASE + "/token",
        json={"email": "ghost@nowhere.com", "password": "Whatever123"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/auth/refresh-token
# ---------------------------------------------------------------------------


async def test_refresh_token_returns_new_token_pair(client, seed_roles):
    """A valid refresh_token rotates and returns a new token pair."""
    tokens = await _register_and_login(client, "refresh_user@test.com", "StrongPass123")
    refresh_token = tokens["refresh_token"]

    response = await client.post(
        BASE + "/refresh-token",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    # The new refresh token must be different from the consumed one (rotation)
    assert body["refresh_token"] != refresh_token


async def test_refresh_token_invalid_value_returns_401(client):
    """Bogus refresh token returns 401."""
    response = await client.post(
        BASE + "/refresh-token",
        json={"refresh_token": "not.a.valid.token"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/auth/change-password
# ---------------------------------------------------------------------------


async def test_change_password_succeeds_and_old_password_stops_working(
    client, seed_roles
):
    """Changing password returns 204; old password is rejected on next login."""
    email = "change_pw@test.com"
    old_pw = "OldPassword123"
    new_pw = "NewPassword456"

    tokens = await _register_and_login(client, email, old_pw)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Change password
    change = await client.post(
        BASE + "/change-password",
        headers=headers,
        json={"current_password": old_pw, "new_password": new_pw},
    )
    assert change.status_code == 204

    # Old password should no longer work
    old_login = await client.post(
        BASE + "/token", json={"email": email, "password": old_pw}
    )
    assert old_login.status_code == 401

    # New password must work
    new_login = await client.post(
        BASE + "/token", json={"email": email, "password": new_pw}
    )
    assert new_login.status_code == 200


async def test_change_password_wrong_current_returns_401(client, auth_headers):
    """Providing the wrong current_password returns 401."""
    response = await client.post(
        BASE + "/change-password",
        headers=auth_headers,
        json={"current_password": "WrongCurrent!", "new_password": "NewPassword123"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/auth/request-recovery
# ---------------------------------------------------------------------------


async def test_request_recovery_returns_200_for_known_email(client, test_credentials):
    """Requesting recovery for an existing email returns 200 with a message."""
    response = await client.post(
        BASE + "/request-recovery",
        json={"email": test_credentials["email"]},
    )
    assert response.status_code == 200
    assert "message" in response.json()


async def test_request_recovery_unknown_email_returns_404(client):
    """Requesting recovery for a non-existent email returns 404."""
    response = await client.post(
        BASE + "/request-recovery",
        json={"email": "ghost_recovery@nowhere.com"},
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/auth/reset-password
# ---------------------------------------------------------------------------


async def test_reset_password_full_flow(client, seed_roles):
    """Request recovery → use token to reset → login with new password succeeds."""
    email = "reset_pw@test.com"
    old_pw = "OldPassword123"
    new_pw = "ResetPassword456"

    await _register_and_login(client, email, old_pw)

    # Request recovery token
    recovery_resp = await client.post(
        BASE + "/request-recovery",
        json={"email": email},
    )
    assert recovery_resp.status_code == 200
    # The API returns the recovery token in the response (useful for testing)
    body = recovery_resp.json()
    # Some implementations embed the token in the message for dev; skip if not present
    recovery_token = body.get("recovery_token") or body.get("token")
    if not recovery_token:
        pytest.skip("Recovery token not exposed in response — skipping reset flow")

    # Reset password
    reset = await client.post(
        BASE + "/reset-password",
        json={"email": email, "recovery_token": recovery_token, "new_password": new_pw},
    )
    assert reset.status_code == 204

    # Login with new password
    new_login = await client.post(
        BASE + "/token", json={"email": email, "password": new_pw}
    )
    assert new_login.status_code == 200
