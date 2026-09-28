"""Skill service for database operations."""

from typing import Optional, Sequence, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.skill.models import Skill, SkillCategory
from src.shared import services as shared_services
from src.shared import exceptions


async def get_skill_by_id(
    session: AsyncSession, skill_id: int, include_deleted: bool = False
) -> Optional[Skill]:
    """Get a skill by ID."""
    return await shared_services.get_one_by_field(
        session, Skill, "id", skill_id, include_deleted
    )


async def get_skills_by_ids(
    session: AsyncSession, skill_ids: List[int], include_deleted: bool = False
) -> Sequence[Skill]:
    """Get multiple skills by IDs."""
    return await shared_services.get_many_by_field(
        session, Skill, "id", skill_ids, include_deleted
    )


async def ensure_skills_exist(
    session: AsyncSession, skill_ids: List[int]
) -> Sequence[Skill]:
    """Ensure all provided skill IDs exist, raising NotFoundException otherwise."""

    if not skill_ids:
        return []

    skills = await get_skills_by_ids(session, skill_ids)
    found_ids = {skill.id for skill in skills}
    missing = set(skill_ids) - found_ids

    if missing:
        raise exceptions.NotFoundException(detail=f"Skills not found: {missing}")

    return skills


async def get_skill_by_name(
    session: AsyncSession, name: str, include_deleted: bool = False
) -> Optional[Skill]:
    """Get a skill by exact name."""
    return await shared_services.get_one_by_field(
        session, Skill, "name", name, include_deleted
    )


async def get_all_skills(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    name_filter: Optional[str] = None,
    category_filter: Optional[SkillCategory] = None,
    include_deleted: bool = False,
) -> Sequence[Skill]:
    """Get all skills with optional filters."""
    stmt = select(Skill)

    if not include_deleted:
        stmt = stmt.where(Skill.deleted_at.is_(None))

    if name_filter:
        stmt = stmt.where(Skill.name.ilike(f"%{name_filter}%"))

    if category_filter:
        stmt = stmt.where(Skill.category == category_filter)

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_skills(
    session: AsyncSession,
    name_filter: Optional[str] = None,
    category_filter: Optional[SkillCategory] = None,
    include_deleted: bool = False,
) -> int:
    """Count skills with optional filters."""
    stmt = select(func.count(Skill.id))

    if not include_deleted:
        stmt = stmt.where(Skill.deleted_at.is_(None))

    if name_filter:
        stmt = stmt.where(Skill.name.ilike(f"%{name_filter}%"))

    if category_filter:
        stmt = stmt.where(Skill.category == category_filter)

    result = await session.execute(stmt)
    return result.unique().scalar_one()


async def create_skill(
    session: AsyncSession, name: str, category: SkillCategory
) -> Skill:
    """Create a new skill."""
    return await shared_services.create(session, Skill, name=name, category=category)


async def update_skill(
    session: AsyncSession,
    skill: Skill,
    name: Optional[str] = None,
    category: Optional[SkillCategory] = None,
) -> Skill:
    """Update skill fields."""
    if name is not None:
        skill.name = name
    if category is not None:
        skill.category = category
    await session.flush()
    return skill


async def delete_skill(
    session: AsyncSession, skill: Skill, hard_delete: bool = False
) -> Skill:
    """Soft delete a skill."""
    return await shared_services.delete(session, skill, hard_delete)


async def restore_skill(session: AsyncSession, skill: Skill) -> Skill:
    """Restore a soft deleted skill."""
    skill.restore()
    await session.flush()
    return skill


async def is_unique_skill_name(
    session: AsyncSession, current_skill: Skill, name: Optional[str] = None
) -> bool:
    """Check if a skill name is unique."""
    existing = False
    if name and name != current_skill.name:
        existing = bool(await get_skill_by_name(session, name, include_deleted=False))
    return not existing
