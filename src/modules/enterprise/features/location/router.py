"""Location router — CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.shared.adapters import get_current_user, require_role
from src.modules.enterprise.shared.dtos import AuthenticatedUser
from src.modules.enterprise.features.location import dtos, handlers
from src.shared.database import sql_client

_require_default_role = require_role(["default"])
router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post("/", response_model=dtos.LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    data: dtos.LocationCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.LocationResponse:
    return await handlers.create_location(session, data)


@router.get("/", response_model=List[dtos.LocationResponse])
async def list_locations(
    country: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.LocationResponse]:
    filters = dtos.LocationFilterParams(
        country=country, state=state, city=city,
        include_deleted=include_deleted, skip=skip, limit=limit,
    )
    return await handlers.list_locations(session, filters)


@router.get("/{location_id}", response_model=dtos.LocationDetailResponse)
async def get_location(
    location_id: int,
    include_deleted: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.LocationDetailResponse:
    return await handlers.get_location(session, location_id, include_deleted)


@router.put("/{location_id}", response_model=dtos.LocationResponse)
async def update_location(
    location_id: int,
    data: dtos.LocationUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.LocationResponse:
    return await handlers.update_location(session, location_id, data)


@router.delete("/{location_id}", response_model=dtos.LocationResponse)
async def delete_location(
    location_id: int,
    hard_delete: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.LocationResponse:
    return await handlers.delete_location(session, location_id, hard_delete)
