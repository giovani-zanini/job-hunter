"""Experience feature router with CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.shared.adapters import get_current_profile_user, require_role
from src.modules.profile.shared.dtos import ProfileUser
from src.modules.profile.features.experience import dtos
from src.modules.profile.features.experience import handlers
from src.shared.database import sql_client
from src.shared import dtos as shared_dtos


_require_default_role = require_role(["default"])
router = APIRouter(prefix="/experiences", tags=["Experiences"])


# --- Experience CRUD ---


@router.post(
    "/",
    response_model=dtos.ExperienceDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new experience",
)
async def create_experience(
    data: dtos.ExperienceCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.ExperienceDetailResponse:
    """Create a new work experience with optional achievements and skills."""
    return await handlers.create_experience(session, current_user.id, data)


@router.get(
    "/",
    response_model=List[dtos.ExperienceResponse],
    summary="List all experiences",
)
async def list_experiences(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    position_title: Optional[str] = Query(
        None, description="Filter by position (partial match)"
    ),
    include_deleted: bool = Query(
        False, description="Include soft deleted experiences"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.ExperienceResponse]:
    """List experiences for the authenticated user."""
    filters = dtos.ExperienceFilterParams(
        user_id=current_user.id,
        company_id=company_id,
        position_title=position_title,
        include_deleted=include_deleted,
        skip=skip,
        limit=limit,
    )
    return await handlers.list_experiences(session, filters)


@router.get(
    "/{experience_id}",
    response_model=dtos.ExperienceDetailResponse,
    summary="Get an experience by ID",
)
async def get_experience(
    experience_id: int,
    include_deleted: bool = Query(False, description="Include if soft deleted"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.ExperienceDetailResponse:
    """Get a specific experience by its ID with achievements."""
    return await handlers.get_experience(
        session, experience_id, include_deleted=include_deleted
    )


@router.put(
    "/{experience_id}",
    response_model=dtos.ExperienceResponse,
    summary="Update an experience",
)
async def update_experience(
    experience_id: int,
    data: dtos.ExperienceUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.ExperienceResponse:
    """Update an experience's information."""
    return await handlers.update_experience(
        session, experience_id, data, current_user.id
    )


@router.delete(
    "/{experience_id}",
    response_model=dtos.ExperienceResponse,
    summary="Delete an experience",
)
async def delete_experience(
    experience_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the experience"),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.ExperienceResponse:
    """Soft delete an experience (or hard delete if specified)."""
    return await handlers.delete_experience(
        session, experience_id, current_user.id, hard_delete=hard_delete
    )


# --- Achievements ---


@router.post(
    "/{experience_id}/achievements",
    response_model=dtos.AchievementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an achievement to an experience",
)
async def add_achievement(
    experience_id: int,
    data: dtos.AchievementInput,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.AchievementResponse:
    """Add an achievement to an experience."""
    return await handlers.add_achievement(session, experience_id, data)


@router.put(
    "/achievements/{achievement_id}",
    response_model=dtos.AchievementResponse,
    summary="Update an achievement",
)
async def update_achievement(
    achievement_id: int,
    data: dtos.AchievementUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.AchievementResponse:
    """Update an achievement's information."""
    return await handlers.update_achievement(session, achievement_id, data)


@router.delete(
    "/achievements/{achievement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an achievement",
)
async def remove_achievement(
    achievement_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> None:
    """Remove an achievement."""
    await handlers.remove_achievement(session, achievement_id)


# --- Experience Skills ---


@router.post(
    "/{experience_id}/skills/{skill_id}",
    response_model=shared_dtos.Message,
    status_code=status.HTTP_201_CREATED,
    summary="Add a skill to an experience",
)
async def add_experience_skill(
    experience_id: int,
    skill_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> shared_dtos.Message:
    """Associate a skill with an experience."""
    return await handlers.add_experience_skill(session, experience_id, skill_id)


@router.delete(
    "/{experience_id}/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a skill from an experience",
)
async def remove_experience_skill(
    experience_id: int,
    skill_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> None:
    """Remove a skill from an experience."""
    await handlers.remove_experience_skill(session, experience_id, skill_id)
