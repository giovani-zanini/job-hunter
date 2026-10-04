"""Anonymous profile ownership against PostgreSQL."""

import asyncio

import pytest
from sqlalchemy import func, select

from src.modules.profile.features.user.models import User
from src.modules.profile.features.user.services import get_or_create_anonymous_user


pytestmark = pytest.mark.asyncio


async def test_reuses_seeded_anonymous_user(db_session):
    first = await get_or_create_anonymous_user(db_session)
    second = await get_or_create_anonymous_user(db_session)
    assert first.id == second.id
    assert first.deleted_at is None


async def test_restores_same_anonymous_user(db_session):
    user = await get_or_create_anonymous_user(db_session)
    original_id = user.id
    user.soft_delete()
    await db_session.flush()

    restored = await get_or_create_anonymous_user(db_session)

    assert restored.id == original_id
    assert restored.deleted_at is None


async def test_concurrent_creation_has_one_anonymous_user(db_session_factory):
    async def resolve():
        async with db_session_factory() as session:
            user = await get_or_create_anonymous_user(session)
            await session.commit()
            return user.id

    ids = await asyncio.gather(resolve(), resolve())
    async with db_session_factory() as session:
        count = await session.scalar(
            select(func.count()).select_from(User).where(User.is_anonymous.is_(True))
        )
    assert ids[0] == ids[1]
    assert count == 1
