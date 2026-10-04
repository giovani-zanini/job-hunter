"""Requirement router — CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.requirement import dtos, handlers
from src.shared.database import sql_client

router = APIRouter(prefix="/requirements", tags=["Requirements"])


@router.post("/", response_model=dtos.RequirementResponse, status_code=status.HTTP_201_CREATED)
async def create_requirement(
    data: dtos.RequirementCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.RequirementResponse:
    return await handlers.create_requirement(session, data)


@router.get("/", response_model=List[dtos.RequirementResponse])
async def list_requirements(
    skill: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
) -> List[dtos.RequirementResponse]:
    filters = dtos.RequirementFilterParams(skill=skill, include_deleted=include_deleted, skip=skip, limit=limit)
    return await handlers.list_requirements(session, filters)


@router.get("/{requirement_id}", response_model=dtos.RequirementDetailResponse)
async def get_requirement(
    requirement_id: int,
    include_deleted: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
) -> dtos.RequirementDetailResponse:
    return await handlers.get_requirement(session, requirement_id, include_deleted)


@router.put("/{requirement_id}", response_model=dtos.RequirementResponse)
async def update_requirement(
    requirement_id: int,
    data: dtos.RequirementUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.RequirementResponse:
    return await handlers.update_requirement(session, requirement_id, data)


@router.delete("/{requirement_id}", response_model=dtos.RequirementResponse)
async def delete_requirement(
    requirement_id: int,
    hard_delete: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.RequirementResponse:
    return await handlers.delete_requirement(session, requirement_id, hard_delete)
