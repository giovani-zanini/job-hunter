"""Vacancy service — database operations."""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.enterprise.features.vacancy.models import (
    Vacancy,
    VacancyRequirement,
    VacancyResponsability,
)
from src.shared import services as shared_services


async def get_all_vacancies(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    title_filter: Optional[str] = None,
    seniority_level_filter: Optional[str] = None,
    company_unit_id_filter: Optional[int] = None,
    include_deleted: bool = False,
) -> Sequence[Vacancy]:
    stmt = select(Vacancy)
    if not include_deleted:
        stmt = stmt.where(Vacancy.deleted_at.is_(None))
    if title_filter:
        stmt = stmt.where(Vacancy.title.ilike(f"%{title_filter}%"))
    if seniority_level_filter:
        stmt = stmt.where(Vacancy.seniority_level == seniority_level_filter)
    if company_unit_id_filter is not None:
        stmt = stmt.where(Vacancy.company_unit_id == company_unit_id_filter)
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_vacancy_with_associations(
    session: AsyncSession, vacancy_id: int, include_deleted: bool = False
) -> Optional[Vacancy]:
    stmt = (
        select(Vacancy)
        .options(
            selectinload(Vacancy.vacancy_requirements),
            selectinload(Vacancy.vacancy_responsabilities),
        )
        .where(Vacancy.id == vacancy_id)
    )
    if not include_deleted:
        stmt = stmt.where(Vacancy.deleted_at.is_(None))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_vacancy(session: AsyncSession, **fields) -> Vacancy:
    return await shared_services.create(session, Vacancy, **fields)


async def update_vacancy(session: AsyncSession, vacancy: Vacancy, **kwargs) -> Vacancy:
    for key, value in kwargs.items():
        if value is not None:
            setattr(vacancy, key, value)
    await session.flush()
    return vacancy


async def delete_vacancy(
    session: AsyncSession, vacancy: Vacancy, hard_delete: bool = False
) -> Vacancy:
    return await shared_services.delete(session, vacancy, hard_delete)


async def add_requirement_to_vacancy(
    session: AsyncSession,
    vacancy_id: int,
    requirement_id: int,
    level: int,
    requirement_type: str,
    optional_requirement_id: Optional[int] = None,
    experience_years: Optional[int] = None,
) -> VacancyRequirement:
    return await shared_services.create(
        session,
        VacancyRequirement,
        vacancy_id=vacancy_id,
        requirement_id=requirement_id,
        optional_requirement_id=optional_requirement_id,
        level=level,
        experience_years=experience_years,
        requirement_type=requirement_type,
    )


async def remove_requirement_from_vacancy(
    session: AsyncSession, vacancy_requirement: VacancyRequirement
) -> None:
    await session.delete(vacancy_requirement)
    await session.flush()


async def get_vacancy_requirement(
    session: AsyncSession, vacancy_requirement_id: int
) -> Optional[VacancyRequirement]:
    result = await session.execute(
        select(VacancyRequirement).where(VacancyRequirement.id == vacancy_requirement_id)
    )
    return result.scalar_one_or_none()


async def add_responsability_to_vacancy(
    session: AsyncSession, vacancy_id: int, responsability_id: int
) -> VacancyResponsability:
    return await shared_services.create(
        session, VacancyResponsability, vacancy_id=vacancy_id, responsability_id=responsability_id
    )


async def remove_responsability_from_vacancy(
    session: AsyncSession, vacancy_responsability: VacancyResponsability
) -> None:
    await session.delete(vacancy_responsability)
    await session.flush()


async def get_vacancy_responsability(
    session: AsyncSession, vacancy_id: int, responsability_id: int
) -> Optional[VacancyResponsability]:
    result = await session.execute(
        select(VacancyResponsability).where(
            VacancyResponsability.vacancy_id == vacancy_id,
            VacancyResponsability.responsability_id == responsability_id,
        )
    )
    return result.scalar_one_or_none()
