from contextlib import asynccontextmanager
from typing import Literal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from src.shared.config import get_settings


_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


def get_engine():
    if not _engine:
        raise RuntimeError("Database not initialized. Call connect_database() first.")
    return _engine


def get_session_factory():
    if not _session_maker:
        raise RuntimeError("Database not initialized. Call connect_database() first.")
    return _session_maker


def connect_to_database():
    global _engine, _session_maker  # NOSONAR pylint: disable=global-statement

    if _engine:
        return

    settings = get_settings()
    _engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    _session_maker = async_sessionmaker(_engine, expire_on_commit=False)


async def disconnect_from_database():
    global _engine, _session_maker  # NOSONAR pylint: disable=global-statement

    if _engine:
        engine = get_engine()
        await engine.dispose()
        _engine = None
        _session_maker = None


@asynccontextmanager
async def get_session(
    session_type: Literal["read", "write", "read-write"] = "read-write",
):
    session_factory = get_session_factory()
    async with session_factory() as session:
        if session_type == "read":
            await session.execute(text("SET TRANSACTION READ ONLY"))

        if session_type == "write":
            await session.execute(text("SET TRANSACTION READ WRITE"))

        try:
            yield session
            if session_type != "read":
                await session.commit()
        except Exception:
            await session.rollback()
            raise


async def test_sql_connection():
    try:
        async with get_session("read") as session:
            await session.execute(text("SELECT 1;"))
    except ConnectionRefusedError as err:
        err.strerror = "Database not connected"
        raise


async def get_sql_read_session():
    async with get_session("read") as session:
        yield session


async def get_sql_default_session():
    async with get_session("read-write") as session:
        yield session
