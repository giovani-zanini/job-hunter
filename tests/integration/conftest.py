"""Disposable PostgreSQL databases for migration and persistence tests."""

import os
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def disposable_database():
    source = os.getenv("TEST_DATABASE_SYNC_URL")
    if not source:
        pytest.skip("TEST_DATABASE_SYNC_URL is required for PostgreSQL integration tests")

    source_url = make_url(source)
    admin_url = source_url.set(database="postgres")
    database_name = f"job_hunter_auth_removal_{uuid4().hex}"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    sync_url = source_url.set(database=database_name)
    async_url = sync_url.set(drivername="postgresql+asyncpg")
    try:
        yield str(sync_url), str(async_url)
    finally:
        with admin_engine.connect() as connection:
            connection.execute(
                text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                     "WHERE datname = :database_name AND pid <> pg_backend_pid()"),
                {"database_name": database_name},
            )
            connection.execute(text(f'DROP DATABASE "{database_name}"'))
        admin_engine.dispose()


@pytest.fixture
def migrated_database(disposable_database, monkeypatch):
    sync_url, async_url = disposable_database
    monkeypatch.setenv("DATABASE_SYNC_URL", sync_url)
    monkeypatch.setenv("DATABASE_URL", async_url)
    config = Config(str(ROOT / "src/shared/database/alembic.ini"))
    command.upgrade(config, "head")
    return sync_url, async_url


@pytest_asyncio.fixture
async def db_session_factory(migrated_database):
    _, async_url = migrated_database
    engine = create_async_engine(async_url)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_session_factory):
    async with db_session_factory() as session:
        yield session
        await session.rollback()
