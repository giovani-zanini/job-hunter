"""Vacancy router — CRUD + sub-resource endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.shared.adapters import get_current_user, require_role
from src.modules.enterprise.shared.dtos import AuthenticatedUser
from src.modules.enterprise.features.vacancy import dtos, handlers
from src.shared.database import sql_client

_require_default_role = require_role(["default"])
router = APIRouter(prefix="/vacancies", tags=["Vacancies"])


@router.post("/", response_model=dtos.VacancyResponse, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    data: dtos.VacancyCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.VacancyResponse:
    return await handlers.create_vacancy(session, data)


@router.get("/", response_model=List[dtos.VacancyResponse])
async def list_vacancies(
    title: Optional[str] = Query(None),
    seniority_level: Optional[str] = Query(None),
    company_unit_id: Optional[int] = Query(None),
    include_deleted: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.VacancyResponse]:
    filters = dtos.VacancyFilterParams(
        title=title,
        seniority_level=seniority_level,
        company_unit_id=company_unit_id,
        include_deleted=include_deleted,
        skip=skip,
        limit=limit,
    )
    return await handlers.list_vacancies(session, filters)


@router.get("/{vacancy_id}", response_model=dtos.VacancyDetailResponse)
async def get_vacancy(
    vacancy_id: int,
    include_deleted: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.VacancyDetailResponse:
    return await handlers.get_vacancy(session, vacancy_id, include_deleted)


@router.put("/{vacancy_id}", response_model=dtos.VacancyResponse)
async def update_vacancy(
    vacancy_id: int,
    data: dtos.VacancyUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.VacancyResponse:
    return await handlers.update_vacancy(session, vacancy_id, data)


@router.delete("/{vacancy_id}", response_model=dtos.VacancyResponse)
async def delete_vacancy(
    vacancy_id: int,
    hard_delete: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.VacancyResponse:
    return await handlers.delete_vacancy(session, vacancy_id, hard_delete)


# --- Requirements sub-resource ---

@router.post(
    "/{vacancy_id}/requirements",
    response_model=dtos.VacancyRequirementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_requirement_to_vacancy(
    vacancy_id: int,
    data: dtos.VacancyRequirementCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.VacancyRequirementResponse:
    return await handlers.add_requirement_to_vacancy(session, vacancy_id, data)


@router.delete("/{vacancy_id}/requirements/{vacancy_requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_requirement_from_vacancy(
    vacancy_id: int,
    vacancy_requirement_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> None:
    await handlers.remove_requirement_from_vacancy(session, vacancy_id, vacancy_requirement_id)


# --- Responsabilities sub-resource ---

@router.post(
    "/{vacancy_id}/responsabilities",
    response_model=dtos.VacancyResponsabilityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_responsability_to_vacancy(
    vacancy_id: int,
    data: dtos.VacancyResponsabilityCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.VacancyResponsabilityResponse:
    return await handlers.add_responsability_to_vacancy(session, vacancy_id, data)


@router.delete(
    "/{vacancy_id}/responsabilities/{responsability_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_responsability_from_vacancy(
    vacancy_id: int,
    responsability_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> None:
    await handlers.remove_responsability_from_vacancy(session, vacancy_id, responsability_id)
