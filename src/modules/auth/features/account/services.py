"""User service for database operations (auth module)."""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.features.account.models import UserAccount
from src.shared import services as shared_services


async def get_all_users(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    email_filter: Optional[str] = None,
) -> Sequence[UserAccount]:
    """Get all users with optional filters."""
    stmt = select(UserAccount)

    if email_filter:
        stmt = stmt.where(UserAccount.email.ilike(f"%{email_filter}%"))

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def create_user(
    session: AsyncSession,
    email: str,
    role_id: int,
) -> UserAccount:
    """Create a new user."""
    return await shared_services.create(session, UserAccount, email=email, role_id=role_id)


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[UserAccount]:
    """Get a user by email."""
    stmt = select(UserAccount).where(UserAccount.email == email)
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()
