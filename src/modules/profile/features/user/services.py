"""User service for database operations."""

from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.user.models import User


async def get_user_by_id(
    session: AsyncSession, user_id: int, include_deleted: bool = False
) -> Optional[User]:
    """Get a user by ID."""
    stmt = select(User).where(User.id == user_id)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_user_by_external_id(
    session: AsyncSession, external_id: int, include_deleted: bool = False
) -> Optional[User]:
    """Get a user by external auth ID."""
    stmt = select(User).where(User.external_id == external_id)
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_all_users(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    external_id_filter: Optional[int] = None,
    include_deleted: bool = False,
) -> Sequence[User]:
    """Get all users with optional filters."""
    stmt = select(User)

    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))

    if external_id_filter is not None:
        stmt = stmt.where(User.external_id == external_id_filter)

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_users(
    session: AsyncSession,
    external_id_filter: Optional[int] = None,
    include_deleted: bool = False,
) -> int:
    """Count users with optional filters."""
    stmt = select(func.count(User.id))

    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))

    if external_id_filter is not None:
        stmt = stmt.where(User.external_id == external_id_filter)

    result = await session.execute(stmt)
    return result.unique().scalar_one()


async def create_user_from_external(session: AsyncSession, external_id: int) -> User:
    """Create a new profile user linked to an auth module user."""
    user = User(external_id=external_id)
    session.add(user)
    await session.flush()
    return user


async def create_user_if_not_exists(
    session: AsyncSession, external_id: int, user: User | None
) -> User:

    if user is None:
        user = await create_user_from_external(session, external_id)
    return user


async def delete_user(
    session: AsyncSession, user: User, hard_delete: bool = False
) -> User:
    """Delete a user, either soft or hard delete."""

    if hard_delete:
        await session.delete(user)
    else:
        user.soft_delete()

    await session.flush()
    return user


async def restore_user(session: AsyncSession, user: User) -> User:
    """Restore a soft deleted user."""
    user.restore()
    await session.flush()
    return user
