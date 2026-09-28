"""Experience service for database operations."""

from datetime import date
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.profile.features.experience.models import (
    Experience,
    Achievements,
    ExperienceSkills,
)
from src.shared import services as shared_services


async def get_experience_by_id(
    session: AsyncSession,
    experience_id: int,
    include_deleted: bool = False,
    load_achievements: bool = False,
) -> Optional[Experience]:
    """Get an experience by ID."""
    stmt = select(Experience).where(Experience.id == experience_id)
    if not include_deleted:
        stmt = stmt.where(Experience.deleted_at.is_(None))
    if load_achievements:
        stmt = stmt.options(selectinload(Experience.achievements))
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_all_experiences(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[int] = None,
    company_id: Optional[int] = None,
    position_title_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[Experience]:
    """Get all experiences with optional filters."""
    stmt = select(Experience)

    if not include_deleted:
        stmt = stmt.where(Experience.deleted_at.is_(None))

    if user_id:
        stmt = stmt.where(Experience.user_id == user_id)

    if company_id:
        stmt = stmt.where(Experience.company_id == company_id)

    if position_title_filter:
        stmt = stmt.where(Experience.position_title.ilike(f"%{position_title_filter}%"))

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_experiences(
    session: AsyncSession,
    user_id: Optional[int] = None,
    company_id: Optional[int] = None,
    position_title_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> int:
    """Count experiences with optional filters."""
    stmt = select(func.count(Experience.id))

    if not include_deleted:
        stmt = stmt.where(Experience.deleted_at.is_(None))

    if user_id:
        stmt = stmt.where(Experience.user_id == user_id)

    if company_id:
        stmt = stmt.where(Experience.company_id == company_id)

    if position_title_filter:
        stmt = stmt.where(Experience.position_title.ilike(f"%{position_title_filter}%"))

    result = await session.execute(stmt)
    return result.unique().scalar_one()


async def create_experience(
    session: AsyncSession,
    user_id: int,
    company_id: int,
    position_title: str,
    start_date: date,
    description: str,
    end_date: Optional[date] = None,
) -> Experience:
    """Create a new experience."""
    return await shared_services.create(
        session,
        Experience,
        user_id=user_id,
        company_id=company_id,
        position_title=position_title,
        start_date=start_date,
        end_date=end_date,
        description=description,
    )


async def update_experience(
    session: AsyncSession,
    experience: Experience,
    company_id: Optional[int] = None,
    position_title: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    description: Optional[str] = None,
) -> Experience:
    """Update experience fields."""
    if company_id is not None:
        experience.company_id = company_id
    if position_title is not None:
        experience.position_title = position_title
    if start_date is not None:
        experience.start_date = start_date
    if end_date is not None:
        experience.end_date = end_date
    if description is not None:
        experience.description = description
    await session.flush()
    return experience


async def delete_experience(
    session: AsyncSession, experience: Experience, hard_delete: bool = False
) -> Experience:
    """Delete an experience (soft or hard delete)."""
    return await shared_services.delete(session, experience, hard_delete)


# --- Achievement Functions ---


async def add_achievement(
    session: AsyncSession,
    experience_id: int,
    title: str,
    description: str,
) -> Achievements:
    """Add an achievement to an experience."""
    return await shared_services.create(
        session,
        Achievements,
        experience_id=experience_id,
        title=title,
        description=description,
    )


async def get_achievement_by_id(
    session: AsyncSession, achievement_id: int
) -> Optional[Achievements]:
    """Get an achievement by ID."""
    return await shared_services.get_one_by_field(
        session, Achievements, "id", achievement_id, True
    )


async def update_achievement(
    session: AsyncSession,
    achievement: Achievements,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Achievements:
    """Update an achievement."""
    if title is not None:
        achievement.title = title
    if description is not None:
        achievement.description = description
    await session.flush()
    return achievement


async def remove_achievement(session: AsyncSession, achievement: Achievements) -> None:
    """Remove an achievement."""
    await session.delete(achievement)
    await session.flush()


# --- Skill Association Functions ---


async def add_experience_skill(
    session: AsyncSession, experience_id: int, skill_id: int
) -> ExperienceSkills:
    """Add a skill to an experience."""
    return await shared_services.create(
        session, ExperienceSkills, experience_id=experience_id, skill_id=skill_id
    )


async def get_experience_skill(
    session: AsyncSession, experience_id: int, skill_id: int
) -> Optional[ExperienceSkills]:
    """Get a specific experience-skill association."""
    stmt = select(ExperienceSkills).where(
        ExperienceSkills.experience_id == experience_id,
        ExperienceSkills.skill_id == skill_id,
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def remove_experience_skill(
    session: AsyncSession, exp_skill: ExperienceSkills
) -> None:
    """Remove a skill from an experience."""
    await session.delete(exp_skill)
    await session.flush()
