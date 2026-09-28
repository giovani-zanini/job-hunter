"""Vacancy use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.vacancy import dtos, services
from src.modules.enterprise.features.vacancy.models import Vacancy
from src.modules.enterprise.features.requirement.models import Requirement
from src.modules.enterprise.features.responsability.models import Responsability
from src.shared import services as shared_services
from src.shared.exceptions import NotFoundException, ConflictException


async def create_vacancy(
    session: AsyncSession, data: dtos.VacancyCreateRequest
) -> dtos.VacancyResponse:
    vacancy = await services.create_vacancy(
        session,
        title=data.title,
        description=data.description,
        company_unit_id=data.company_unit_id,
        contract_id=data.contract_id,
        seniority_level=data.seniority_level,
        published_date=data.published_date,
        custom_data=data.custom_data,
    )
    await session.refresh(vacancy)
    return dtos.VacancyResponse.model_validate(vacancy)


async def get_vacancy(
    session: AsyncSession, vacancy_id: int, include_deleted: bool = False
) -> dtos.VacancyDetailResponse:
    vacancy = await services.get_vacancy_with_associations(session, vacancy_id, include_deleted)
    if vacancy is None:
        raise NotFoundException(detail=f"Vacancy {vacancy_id} not found")
    return dtos.VacancyDetailResponse.model_validate(vacancy)


async def list_vacancies(
    session: AsyncSession, filters: dtos.VacancyFilterParams
) -> list[dtos.VacancyResponse]:
    vacancies = await services.get_all_vacancies(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        title_filter=filters.title,
        seniority_level_filter=filters.seniority_level,
        company_unit_id_filter=filters.company_unit_id,
        include_deleted=filters.include_deleted,
    )
    return [dtos.VacancyResponse.model_validate(v) for v in vacancies]


async def update_vacancy(
    session: AsyncSession, vacancy_id: int, data: dtos.VacancyUpdateRequest
) -> dtos.VacancyResponse:
    vacancy = await shared_services.ensure_exists(
        session, Vacancy, vacancy_id, label="Vacancy"
    )
    vacancy = await services.update_vacancy(
        session,
        vacancy,
        title=data.title,
        description=data.description,
        company_unit_id=data.company_unit_id,
        contract_id=data.contract_id,
        seniority_level=data.seniority_level,
        published_date=data.published_date,
        custom_data=data.custom_data,
    )
    await session.refresh(vacancy)
    return dtos.VacancyResponse.model_validate(vacancy)


async def delete_vacancy(
    session: AsyncSession, vacancy_id: int, hard_delete: bool = False
) -> dtos.VacancyResponse:
    vacancy = await shared_services.ensure_exists(
        session, Vacancy, vacancy_id, include_deleted=True, label="Vacancy"
    )
    if hard_delete:
        response = dtos.VacancyResponse.model_validate(vacancy)
        await services.delete_vacancy(session, vacancy, hard_delete=True)
        return response
    vacancy = await services.delete_vacancy(session, vacancy)
    await session.refresh(vacancy)
    return dtos.VacancyResponse.model_validate(vacancy)


# --- Requirements association ---

async def add_requirement_to_vacancy(
    session: AsyncSession, vacancy_id: int, data: dtos.VacancyRequirementCreateRequest
) -> dtos.VacancyRequirementResponse:
    await shared_services.ensure_exists(session, Vacancy, vacancy_id, label="Vacancy")
    await shared_services.ensure_exists(session, Requirement, data.requirement_id, label="Requirement")
    if data.optional_requirement_id is not None:
        await shared_services.ensure_exists(
            session, Requirement, data.optional_requirement_id, label="OptionalRequirement"
        )
    vr = await services.add_requirement_to_vacancy(
        session,
        vacancy_id=vacancy_id,
        requirement_id=data.requirement_id,
        optional_requirement_id=data.optional_requirement_id,
        level=data.level,
        experience_years=data.experience_years,
        requirement_type=data.requirement_type,
    )
    await session.refresh(vr)
    return dtos.VacancyRequirementResponse.model_validate(vr)


async def remove_requirement_from_vacancy(
    session: AsyncSession, vacancy_id: int, vacancy_requirement_id: int
) -> None:
    await shared_services.ensure_exists(session, Vacancy, vacancy_id, label="Vacancy")
    vr = await services.get_vacancy_requirement(session, vacancy_requirement_id)
    if vr is None or vr.vacancy_id != vacancy_id:
        raise NotFoundException(detail=f"VacancyRequirement {vacancy_requirement_id} not found for vacancy {vacancy_id}")
    await services.remove_requirement_from_vacancy(session, vr)


# --- Responsabilities association ---

async def add_responsability_to_vacancy(
    session: AsyncSession, vacancy_id: int, data: dtos.VacancyResponsabilityCreateRequest
) -> dtos.VacancyResponsabilityResponse:
    await shared_services.ensure_exists(session, Vacancy, vacancy_id, label="Vacancy")
    await shared_services.ensure_exists(session, Responsability, data.responsability_id, label="Responsability")
    existing = await services.get_vacancy_responsability(session, vacancy_id, data.responsability_id)
    if existing is not None:
        raise ConflictException(detail=f"Responsability {data.responsability_id} already linked to vacancy {vacancy_id}")
    vr = await services.add_responsability_to_vacancy(session, vacancy_id, data.responsability_id)
    await session.refresh(vr)
    return dtos.VacancyResponsabilityResponse.model_validate(vr)


async def remove_responsability_from_vacancy(
    session: AsyncSession, vacancy_id: int, responsability_id: int
) -> None:
    await shared_services.ensure_exists(session, Vacancy, vacancy_id, label="Vacancy")
    vr = await services.get_vacancy_responsability(session, vacancy_id, responsability_id)
    if vr is None:
        raise NotFoundException(detail=f"Responsability {responsability_id} not linked to vacancy {vacancy_id}")
    await services.remove_responsability_from_vacancy(session, vr)
