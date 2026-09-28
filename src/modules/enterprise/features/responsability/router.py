"""Responsability router — CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.shared.adapters import get_current_user, require_role
from src.modules.enterprise.shared.dtos import AuthenticatedUser
from src.modules.enterprise.features.responsability import dtos, handlers
from src.shared.database import sql_client

_require_default_role = require_role(["default"])
router = APIRouter(prefix="/responsabilities", tags=["Responsabilities"])


@router.post("/", response_model=dtos.ResponsabilityResponse, status_code=status.HTTP_201_CREATED)
async def create_responsability(
    data: dtos.ResponsabilityCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.ResponsabilityResponse:
    return await handlers.create_responsability(session, data)


@router.get("/", response_model=List[dtos.ResponsabilityResponse])
async def list_responsabilities(
    action: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.ResponsabilityResponse]:
    filters = dtos.ResponsabilityFilterParams(action=action, include_deleted=include_deleted, skip=skip, limit=limit)
    return await handlers.list_responsabilities(session, filters)


@router.get("/{responsability_id}", response_model=dtos.ResponsabilityDetailResponse)
async def get_responsability(
    responsability_id: int,
    include_deleted: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.ResponsabilityDetailResponse:
    return await handlers.get_responsability(session, responsability_id, include_deleted)


@router.put("/{responsability_id}", response_model=dtos.ResponsabilityResponse)
async def update_responsability(
    responsability_id: int,
    data: dtos.ResponsabilityUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.ResponsabilityResponse:
    return await handlers.update_responsability(session, responsability_id, data)


@router.delete("/{responsability_id}", response_model=dtos.ResponsabilityResponse)
async def delete_responsability(
    responsability_id: int,
    hard_delete: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.ResponsabilityResponse:
    return await handlers.delete_responsability(session, responsability_id, hard_delete)
