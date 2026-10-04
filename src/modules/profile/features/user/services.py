"""Persistence operations for local profile owners."""

from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.user.models import User


async def get_or_create_anonymous_user(session: AsyncSession) -> User:
    """Return the single anonymous owner, restoring it after soft deletion."""
    statement = (
        insert(User)
        .values(is_anonymous=True)
        .on_conflict_do_update(
            index_elements=[User.is_anonymous],
            index_where=User.is_anonymous.is_(True),
            set_={"deleted_at": None},
        )
        .returning(User.id)
    )
    user_id = await session.scalar(statement)
    user = await session.get(User, user_id)
    if user is None:
        raise RuntimeError("Anonymous user could not be resolved")
    await session.refresh(user)
    return user


async def get_user_by_id(
    session: AsyncSession, user_id: int, include_deleted: bool = False
) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    return (await session.execute(stmt)).unique().scalar_one_or_none()


async def get_all_users(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    is_anonymous_filter: Optional[bool] = None,
    include_deleted: bool = False,
) -> Sequence[User]:
    stmt = select(User)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    if is_anonymous_filter is not None:
        stmt = stmt.where(User.is_anonymous == is_anonymous_filter)
    return (await session.execute(stmt.offset(skip).limit(limit))).scalars().all()


async def count_users(
    session: AsyncSession,
    is_anonymous_filter: Optional[bool] = None,
    include_deleted: bool = False,
) -> int:
    stmt = select(func.count(User.id))
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    if is_anonymous_filter is not None:
        stmt = stmt.where(User.is_anonymous == is_anonymous_filter)
    return (await session.execute(stmt)).unique().scalar_one()


async def delete_user(
    session: AsyncSession, user: User, hard_delete: bool = False
) -> User:
    if hard_delete:
        await session.delete(user)
    else:
        user.soft_delete()
    await session.flush()
    return user


async def restore_user(session: AsyncSession, user: User) -> User:
    user.restore()
    await session.flush()
    return user
