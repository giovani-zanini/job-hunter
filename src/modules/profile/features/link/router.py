"""Link feature router with CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.shared.adapters import get_current_profile_user, require_role
from src.modules.profile.shared.dtos import ProfileUser
from src.modules.profile.features.link import dtos
from src.modules.profile.features.link import handlers
from src.shared.database import sql_client


_require_default_role = require_role(["default"])
router = APIRouter(prefix="/links", tags=["Links"])


# --- Link CRUD ---


@router.post(
    "/",
    response_model=dtos.LinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new link",
)
async def create_link(
    data: dtos.LinkCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.LinkResponse:
    """Create a new link for the authenticated user."""
    return await handlers.create_link(session, current_user.id, data)


@router.get(
    "/",
    response_model=List[dtos.LinkResponse],
    summary="List all links",
)
async def list_links(
    type: Optional[dtos.LinkType] = Query(
        None, alias="type", description="Filter by link type"
    ),
    from_: Optional[str] = Query(
        None, alias="from", description="Filter by origin (partial match)"
    ),
    include_deleted: bool = Query(False, description="Include soft deleted links"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.LinkResponse]:
    """List links for the authenticated user."""
    filters = dtos.LinkFilterParams(
        user_id=current_user.id,
        type=type,
        from_=from_,
        include_deleted=include_deleted,
        skip=skip,
        limit=limit,
    )
    return await handlers.list_links(session, filters)


@router.get(
    "/{link_id}",
    response_model=dtos.LinkDetailResponse,
    summary="Get a link by ID",
)
async def get_link(
    link_id: int,
    include_deleted: bool = Query(False, description="Include if soft deleted"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.LinkDetailResponse:
    """Get a specific link by its ID."""
    return await handlers.get_link(session, link_id, include_deleted)


@router.put(
    "/{link_id}",
    response_model=dtos.LinkResponse,
    summary="Update a link",
)
async def update_link(
    link_id: int,
    data: dtos.LinkUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.LinkResponse:
    """Update a link's information."""
    return await handlers.update_link(session, link_id, data, current_user.id)


@router.delete(
    "/{link_id}",
    response_model=dtos.LinkResponse,
    summary="Delete a link",
)
async def delete_link(
    link_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the link"),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.LinkResponse:
    """Soft delete a link (or hard delete if specified)."""
    return await handlers.delete_link(session, link_id, current_user.id, hard_delete)
