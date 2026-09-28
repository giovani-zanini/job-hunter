"""Requirement service — database operations."""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.requirement.models import Requirement
from src.shared import services as shared_services


async def get_all_requirements(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    skill_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[Requirement]:
    stmt = select(Requirement)
    if not include_deleted:
        stmt = stmt.where(Requirement.deleted_at.is_(None))
    if skill_filter:
        stmt = stmt.where(Requirement.skill.ilike(f"%{skill_filter}%"))
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_requirement(session: AsyncSession, skill: str) -> Requirement:
    return await shared_services.create(session, Requirement, skill=skill)


async def update_requirement(
    session: AsyncSession, requirement: Requirement, skill: Optional[str] = None
) -> Requirement:
    if skill is not None:
        requirement.skill = skill
    await session.flush()
    return requirement


async def delete_requirement(
    session: AsyncSession, requirement: Requirement, hard_delete: bool = False
) -> Requirement:
    return await shared_services.delete(session, requirement, hard_delete)
