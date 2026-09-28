"""Segment router — CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.shared.adapters import get_current_user, require_role
from src.modules.enterprise.shared.dtos import AuthenticatedUser
from src.modules.enterprise.features.segment import dtos, handlers
from src.shared.database import sql_client

_require_default_role = require_role(["default"])
router = APIRouter(prefix="/segments", tags=["Segments"])


@router.post("/", response_model=dtos.SegmentResponse, status_code=status.HTTP_201_CREATED)
async def create_segment(
    data: dtos.SegmentCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.SegmentResponse:
    return await handlers.create_segment(session, data)


@router.get("/", response_model=List[dtos.SegmentResponse])
async def list_segments(
    name: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.SegmentResponse]:
    filters = dtos.SegmentFilterParams(name=name, include_deleted=include_deleted, skip=skip, limit=limit)
    return await handlers.list_segments(session, filters)


@router.get("/{segment_id}", response_model=dtos.SegmentDetailResponse)
async def get_segment(
    segment_id: int,
    include_deleted: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.SegmentDetailResponse:
    return await handlers.get_segment(session, segment_id, include_deleted)


@router.put("/{segment_id}", response_model=dtos.SegmentResponse)
async def update_segment(
    segment_id: int,
    data: dtos.SegmentUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.SegmentResponse:
    return await handlers.update_segment(session, segment_id, data)


@router.delete("/{segment_id}", response_model=dtos.SegmentResponse)
async def delete_segment(
    segment_id: int,
    hard_delete: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.SegmentResponse:
    return await handlers.delete_segment(session, segment_id, hard_delete)
