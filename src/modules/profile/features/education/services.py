"""Education service for database operations."""

from datetime import date
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.education.models import Education, EducationSkills
from src.shared import services as shared_services


async def get_education_by_id(
    session: AsyncSession, education_id: int, include_deleted: bool = False
) -> Optional[Education]:
    """Get an education by ID."""
    return await shared_services.get_one_by_field(
        session, Education, "id", education_id, include_deleted
    )


async def get_all_education(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[int] = None,
    institution_name_filter: Optional[str] = None,
    degree_filter: Optional[str] = None,
    field_of_study_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[Education]:
    """Get all education records with optional filters."""
    stmt = select(Education)

    if not include_deleted:
        stmt = stmt.where(Education.deleted_at.is_(None))

    if user_id:
        stmt = stmt.where(Education.user_id == user_id)

    if institution_name_filter:
        stmt = stmt.where(
            Education.institution_name.ilike(f"%{institution_name_filter}%")
        )

    if degree_filter:
        stmt = stmt.where(Education.degree.ilike(f"%{degree_filter}%"))

    if field_of_study_filter:
        stmt = stmt.where(Education.field_of_study.ilike(f"%{field_of_study_filter}%"))

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_education(
    session: AsyncSession,
    user_id: Optional[int] = None,
    institution_name_filter: Optional[str] = None,
    degree_filter: Optional[str] = None,
    field_of_study_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> int:
    """Count education records with optional filters."""
    stmt = select(func.count(Education.id))

    if not include_deleted:
        stmt = stmt.where(Education.deleted_at.is_(None))

    if user_id:
        stmt = stmt.where(Education.user_id == user_id)

    if institution_name_filter:
        stmt = stmt.where(
            Education.institution_name.ilike(f"%{institution_name_filter}%")
        )

    if degree_filter:
        stmt = stmt.where(Education.degree.ilike(f"%{degree_filter}%"))

    if field_of_study_filter:
        stmt = stmt.where(Education.field_of_study.ilike(f"%{field_of_study_filter}%"))

    result = await session.execute(stmt)
    return result.unique().scalar_one()


async def create_education(
    session: AsyncSession,
    user_id: int,
    institution_name: str,
    degree: str,
    field_of_study: str,
    start_date: date,
    end_date: date,
) -> Education:
    """Create a new education record."""
    return await shared_services.create(
        session,
        Education,
        user_id=user_id,
        institution_name=institution_name,
        degree=degree,
        field_of_study=field_of_study,
        start_date=start_date,
        end_date=end_date,
    )


async def update_education(
    session: AsyncSession,
    education: Education,
    institution_name: Optional[str] = None,
    degree: Optional[str] = None,
    field_of_study: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Education:
    """Update education fields."""
    if institution_name is not None:
        education.institution_name = institution_name
    if degree is not None:
        education.degree = degree
    if field_of_study is not None:
        education.field_of_study = field_of_study
    if start_date is not None:
        education.start_date = start_date
    if end_date is not None:
        education.end_date = end_date
    await session.flush()
    return education


async def delete_education(
    session: AsyncSession, education: Education, hard_delete: bool = False
) -> Education:
    """Delete an education record (soft or hard delete)."""
    return await shared_services.delete(session, education, hard_delete)


# --- Skill Association Functions ---


async def add_education_skill(
    session: AsyncSession, education_id: int, skill_id: int
) -> EducationSkills:
    """Add a skill to an education."""
    return await shared_services.create(
        session, EducationSkills, education_id=education_id, skill_id=skill_id
    )


async def get_education_skill(
    session: AsyncSession, education_id: int, skill_id: int
) -> Optional[EducationSkills]:
    """Get a specific education-skill association."""
    stmt = select(EducationSkills).where(
        EducationSkills.education_id == education_id,
        EducationSkills.skill_id == skill_id,
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def remove_education_skill(
    session: AsyncSession, edu_skill: EducationSkills
) -> None:
    """Remove a skill from an education."""
    await session.delete(edu_skill)
    await session.flush()
