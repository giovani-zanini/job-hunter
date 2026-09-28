"""Company router — CRUD + unit/segment sub-routes."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.shared.adapters import get_current_user, require_role
from src.modules.enterprise.shared.dtos import AuthenticatedUser
from src.modules.enterprise.features.company import dtos, handlers
from src.shared.database import sql_client

_require_default_role = require_role(["default"])
router = APIRouter(prefix="/enterprise/companies", tags=["Enterprise Companies"])


# --- Company CRUD ---

@router.post("/", response_model=dtos.CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: dtos.CompanyCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.CompanyResponse:
    return await handlers.create_company(session, data)


@router.get("/", response_model=List[dtos.CompanyResponse])
async def list_companies(
    name: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.CompanyResponse]:
    filters = dtos.CompanyFilterParams(name=name, include_deleted=include_deleted, skip=skip, limit=limit)
    return await handlers.list_companies(session, filters)


@router.get("/{company_id}", response_model=dtos.CompanyDetailResponse)
async def get_company(
    company_id: int,
    include_deleted: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.CompanyDetailResponse:
    return await handlers.get_company(session, company_id, include_deleted)


@router.put("/{company_id}", response_model=dtos.CompanyResponse)
async def update_company(
    company_id: int,
    data: dtos.CompanyUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.CompanyResponse:
    return await handlers.update_company(session, company_id, data)


@router.delete("/{company_id}", response_model=dtos.CompanyResponse)
async def delete_company(
    company_id: int,
    hard_delete: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.CompanyResponse:
    return await handlers.delete_company(session, company_id, hard_delete)


# --- CompanyUnit sub-routes ---

@router.post(
    "/{company_id}/units",
    response_model=dtos.CompanyUnitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_unit(
    company_id: int,
    data: dtos.CompanyUnitCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.CompanyUnitResponse:
    return await handlers.add_unit(session, company_id, data)


@router.get("/{company_id}/units", response_model=List[dtos.CompanyUnitResponse])
async def list_units(
    company_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.CompanyUnitResponse]:
    return await handlers.list_units(session, company_id)


@router.delete("/{company_id}/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_unit(
    company_id: int,
    unit_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> None:
    await handlers.remove_unit(session, company_id, unit_id)


# --- CompanySegment sub-routes ---

@router.post(
    "/{company_id}/segments",
    response_model=dtos.CompanySegmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_segment(
    company_id: int,
    data: dtos.CompanySegmentCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.CompanySegmentResponse:
    return await handlers.add_segment(session, company_id, data.segment_id)


@router.get("/{company_id}/segments", response_model=List[dtos.CompanySegmentResponse])
async def list_segments(
    company_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.CompanySegmentResponse]:
    return await handlers.list_segments(session, company_id)


@router.delete("/{company_id}/segments/{segment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_segment(
    company_id: int,
    segment_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> None:
    await handlers.remove_segment(session, company_id, segment_id)
