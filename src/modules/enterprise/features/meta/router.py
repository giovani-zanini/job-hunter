"""Meta router — CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.meta import dtos, handlers
from src.shared.database import sql_client

router = APIRouter(prefix="/metas", tags=["Metas"])


@router.post("/", response_model=dtos.MetaResponse, status_code=status.HTTP_201_CREATED)
async def create_meta(
    data: dtos.MetaCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.MetaResponse:
    return await handlers.create_meta(session, data)


@router.get("/", response_model=List[dtos.MetaResponse])
async def list_metas(
    vacancy_id: Optional[int] = Query(None),
    company_id: Optional[int] = Query(None),
    include_deleted: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
) -> List[dtos.MetaResponse]:
    filters = dtos.MetaFilterParams(
        vacancy_id=vacancy_id,
        company_id=company_id,
        include_deleted=include_deleted,
        skip=skip,
        limit=limit,
    )
    return await handlers.list_metas(session, filters)


@router.get("/{meta_id}", response_model=dtos.MetaDetailResponse)
async def get_meta(
    meta_id: int,
    include_deleted: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
) -> dtos.MetaDetailResponse:
    return await handlers.get_meta(session, meta_id, include_deleted)


@router.put("/{meta_id}", response_model=dtos.MetaResponse)
async def update_meta(
    meta_id: int,
    data: dtos.MetaUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.MetaResponse:
    return await handlers.update_meta(session, meta_id, data)


@router.delete("/{meta_id}", response_model=dtos.MetaResponse)
async def delete_meta(
    meta_id: int,
    hard_delete: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.MetaResponse:
    return await handlers.delete_meta(session, meta_id, hard_delete)
