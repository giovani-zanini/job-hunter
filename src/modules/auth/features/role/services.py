"""Role service for database operations."""

from typing import Optional, Sequence

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared import exceptions
from src.modules.auth.features.account.models import UserAccount
from src.modules.auth.features.role.models import Role
from src.modules.auth.features.role import dtos
from src.shared import services as shared_services


async def get_all_roles(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    name_filter: Optional[str] = None,
) -> Sequence[Role]:
    """Get all roles with optional filters."""
    stmt = select(Role)

    if name_filter:
        stmt = stmt.where(Role.name.ilike(f"%{name_filter}%"))

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_role(
    session: AsyncSession, name: str, description: Optional[str] = None
) -> Role:
    """Create a new role."""
    return await shared_services.create(
        session, Role, name=name, description=description
    )


async def update_role(
    session: AsyncSession,
    role: Role,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Role:
    """Update role fields."""
    if name is not None:
        role.name = name
    if description is not None:
        role.description = description
    await session.flush()
    return role


async def delete_role(session: AsyncSession, role: Role) -> None:
    """Hard delete a role."""
    await session.delete(role)
    await session.flush()


async def get_role_by_user_id(db_session: AsyncSession, user_id: int) -> Role:
    stmt = (
        select(Role)
        .join(UserAccount, Role.id == UserAccount.role_id)
        .where(and_(UserAccount.id == user_id, UserAccount.is_active.is_(True)))
    )
    result = await db_session.execute(stmt)
    result = result.unique().scalar_one_or_none()
    if not result:
        raise exceptions.AppException()
    return result
