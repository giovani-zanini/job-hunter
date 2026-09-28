"""Global E2E test configuration and fixtures.

Execution model
---------------
- The .env.test file is loaded via ``pytest_configure`` hook, which runs
  before any src.* module is imported. This ensures pyantic-settings
  singletons (app_settings, auth_settings) pick up the test values.
- A single session-scoped ``AsyncClient`` wraps the real FastAPI app with
  ``LifespanManager`` so startup/shutdown events (DB connection) are fired.
- One test user is registered and logged in once per session; all tests
  receive the same ``auth_headers`` dict.
- Profile tables are truncated BEFORE each test function to guarantee
  clean state, while auth tables persist for the whole session.
"""

from __future__ import annotations

from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Load test environment variables before any src.* import
# ---------------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:  # noqa: D401
    """Load .env.test into the process environment early enough that
    pydantic-settings singletons read the test values on first import."""
    env_file = Path(__file__).parent.parent / ".env.test"
    load_dotenv(str(env_file), override=True)


# ---------------------------------------------------------------------------
# App + HTTP client
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session")
async def app_instance():
    """Import the FastAPI application after env vars are loaded."""
    from src.main import app  # noqa: PLC0415

    return app


@pytest_asyncio.fixture(scope="session")
async def client(app_instance) -> AsyncGenerator:
    """Session-scoped AsyncClient that triggers FastAPI lifespan events."""
    from asgi_lifespan import LifespanManager
    from httpx import ASGITransport, AsyncClient

    async with LifespanManager(app_instance) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://test",
        ) as http_client:
            yield http_client


# ---------------------------------------------------------------------------
# Database seeding (roles must exist before any user can register)
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session", autouse=True)
async def seed_roles(client):  # noqa: ARG001
    """Truncate all auth tables, then seed roles once per session.

    Starting with a clean auth schema prevents 409 conflicts when the same
    test emails are used across multiple pytest runs against a persistent DB.
    """
    from sqlalchemy import text

    from src.modules.auth.seed import seed_roles
    from src.modules.auth.features.role.dtos import CreateRoleRequest
    from src.shared.database import sql_client

    async with sql_client.get_session("read-write") as session:
        # Wipe all auth data so each test session starts completely fresh
        await session.execute(
            text(
                'TRUNCATE TABLE auth."Session", auth."Auth", auth."User", auth."Role" CASCADE'
            )
        )

    async with sql_client.get_session("read-write") as session:
        await seed_roles(
            session,
            [
                CreateRoleRequest(name="admin", description="Administrator role"),
                CreateRoleRequest(name="default", description="Default user role"),
            ],
        )


# ---------------------------------------------------------------------------
# Shared test user
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session")
async def test_credentials(client, seed_roles) -> dict:  # noqa: ARG001
    """Register a shared test user (ignores 409 if it already exists)."""
    email = "e2etest@example.com"
    password = "Test@Password123"

    response = await client.post(
        "/api/v1/account/",
        json={"email": email, "password": password},
    )
    # 201 = newly created; 409 = already exists from a previous run — both are fine
    assert response.status_code in (201, 409), response.text
    return {"email": email, "password": password}


@pytest_asyncio.fixture(scope="session")
async def auth_headers(client, test_credentials) -> dict:
    """Login once and return Bearer headers reused by all tests."""
    response = await client.post("/api/v1/auth/token", json=test_credentials)
    assert response.status_code == 200, response.text
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


# ---------------------------------------------------------------------------
# Per-test profile table cleanup
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(autouse=True)
async def cleanup_profile_tables(client):  # noqa: ARG001
    """Truncate all profile-schema tables before each test to ensure isolation.

    The ``profile.User`` row is intentionally kept so the session-level
    ``auth_headers`` fixture remains valid across the entire session.
    """
    from sqlalchemy import text

    from src.shared.database import sql_client

    async def _truncate() -> None:
        async with sql_client.get_session("read-write") as session:
            await session.execute(
                text(
                    """
                    TRUNCATE TABLE
                        "profile"."Profile",
                        "profile"."Skill",
                        "profile"."Company",
                        "profile"."Link",
                        "profile"."Experience",
                        "profile"."Education",
                        "profile"."Certificate"
                    CASCADE
                    """
                )
            )

    await _truncate()
    yield


# ---------------------------------------------------------------------------
# Per-test enterprise table cleanup
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(autouse=True)
async def cleanup_enterprise_tables(client):  # noqa: ARG001
    """Truncate all enterprise-schema tables before each test."""
    from sqlalchemy import text

    from src.shared.database import sql_client

    async def _truncate() -> None:
        async with sql_client.get_session("read-write") as session:
            await session.execute(
                text(
                    """
                    TRUNCATE TABLE
                        "enterprise"."Meta",
                        "enterprise"."VacancyRequirement",
                        "enterprise"."VacancyResponsability",
                        "enterprise"."Vacancy",
                        "enterprise"."CompanySegment",
                        "enterprise"."CompanyUnit",
                        "enterprise"."Company",
                        "enterprise"."Contract",
                        "enterprise"."Requirement",
                        "enterprise"."Responsability",
                        "enterprise"."Segment",
                        "enterprise"."Location"
                    CASCADE
                    """
                )
            )

    await _truncate()
    yield
