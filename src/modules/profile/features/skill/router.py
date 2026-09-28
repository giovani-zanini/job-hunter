"""Skill feature router with CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.shared.adapters import get_current_profile_user, require_role
from src.modules.profile.shared.dtos import ProfileUser
from src.modules.profile.features.skill import dtos
from src.modules.profile.features.skill import handlers
from src.shared.database import sql_client


_require_default_role = require_role(["default"])
router = APIRouter(prefix="/skills", tags=["Skills"])


@router.post(
    "/",
    response_model=dtos.SkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new skill",
)
async def create_skill(
    data: dtos.SkillCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.SkillResponse:
    """Create a new skill with the provided name and category."""
    return await handlers.create_skill(session, data)


@router.get(
    "/",
    response_model=List[dtos.SkillResponse],
    summary="List all skills",
)
async def list_skills(
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    category: Optional[dtos.SkillCategory] = Query(
        None, description="Filter by category"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.SkillResponse]:
    """List all skills with optional filters and pagination."""
    filters = dtos.SkillFilterParams(
        name=name,
        category=category,
        skip=skip,
        limit=limit,
    )
    return await handlers.list_skills(session, filters)


@router.get(
    "/{skill_id}",
    response_model=dtos.SkillDetailResponse,
    summary="Get a skill by ID",
)
async def get_skill(
    skill_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.SkillDetailResponse:
    """Get a specific skill by its ID."""
    return await handlers.get_skill(session, skill_id)


@router.put(
    "/{skill_id}",
    response_model=dtos.SkillResponse,
    summary="Update a skill",
)
async def update_skill(
    skill_id: int,
    data: dtos.SkillUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.SkillResponse:
    """Update a skill's information."""
    return await handlers.update_skill(session, skill_id, data)


@router.delete(
    "/{skill_id}",
    response_model=dtos.SkillResponse,
    summary="Delete a skill",
)
async def delete_skill(
    skill_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.SkillResponse:
    """Soft delete a skill (or hard delete if specified)."""
    return await handlers.delete_skill(session, skill_id)
