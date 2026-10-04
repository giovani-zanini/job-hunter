"""Database-backed E2E fixtures."""

import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio

# ---------------------------------------------------------------------------
# App + HTTP client
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session")
async def app_instance():
    """Import the FastAPI application after env vars are loaded."""
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is required for PostgreSQL E2E tests")
    os.environ["DATABASE_URL"] = database_url
    from src.shared.config import get_settings
    get_settings.cache_clear()
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
# Per-test profile table cleanup
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(autouse=True)
async def cleanup_profile_tables(client):  # noqa: ARG001
    """Truncate all profile-schema tables before each test to ensure isolation.

    The anonymous ``profile.User`` row is kept across requests.
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
