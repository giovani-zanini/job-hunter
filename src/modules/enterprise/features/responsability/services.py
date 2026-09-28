"""Responsability service — database operations."""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.responsability.models import Responsability
from src.shared import services as shared_services


async def get_all_responsabilities(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    action_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[Responsability]:
    stmt = select(Responsability)
    if not include_deleted:
        stmt = stmt.where(Responsability.deleted_at.is_(None))
    if action_filter:
        stmt = stmt.where(Responsability.action.ilike(f"%{action_filter}%"))
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_responsability(
    session: AsyncSession, action: str, target: str, outcome: str
) -> Responsability:
    return await shared_services.create(session, Responsability, action=action, target=target, outcome=outcome)


async def update_responsability(
    session: AsyncSession,
    responsability: Responsability,
    action: Optional[str] = None,
    target: Optional[str] = None,
    outcome: Optional[str] = None,
) -> Responsability:
    if action is not None:
        responsability.action = action
    if target is not None:
        responsability.target = target
    if outcome is not None:
        responsability.outcome = outcome
    await session.flush()
    return responsability


async def delete_responsability(
    session: AsyncSession, responsability: Responsability, hard_delete: bool = False
) -> Responsability:
    return await shared_services.delete(session, responsability, hard_delete)
