"""Profile feature router with CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.shared.adapters import get_current_profile_user, require_role
from src.modules.profile.shared.dtos import ProfileUser
from src.modules.profile.features.profile import dtos
from src.modules.profile.features.profile import handlers
from src.shared.database import sql_client
from src.shared import dtos as shared_dtos


_require_default_role = require_role(["default"])
router = APIRouter(prefix="/profiles", tags=["Profiles"])


# --- Profile CRUD ---


@router.post(
    "/",
    response_model=dtos.ProfileDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new profile",
)
async def create_profile(
    data: dtos.ProfileCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.ProfileDetailResponse:
    """Create a new profile for the authenticated user with optional skills and links."""
    return await handlers.create_profile(session, current_user.id, data)


@router.get(
    "/",
    response_model=List[dtos.ProfileResponse],
    summary="List all profiles",
)
async def list_profiles(
    slug: Optional[str] = Query(None, description="Filter by slug (partial match)"),
    full_name: Optional[str] = Query(
        None, description="Filter by full name (partial match)"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.ProfileResponse]:
    """List profiles for the authenticated user."""
    filters = dtos.ProfileFilterParams(
        user_id=current_user.id,
        slug=slug,
        full_name=full_name,
        skip=skip,
        limit=limit,
    )
    return await handlers.list_profiles(session, filters)


@router.get(
    "/{profile_id}",
    response_model=dtos.ProfileDetailResponse,
    summary="Get a profile by ID",
)
async def get_profile(
    profile_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.ProfileDetailResponse:
    """Get a specific profile by its ID with associated skills."""
    return await handlers.get_profile(session, profile_id)


@router.put(
    "/{profile_id}",
    response_model=dtos.ProfileResponse,
    summary="Update a profile",
)
async def update_profile(
    profile_id: int,
    data: dtos.ProfileUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.ProfileResponse:
    """Update a profile's information."""
    return await handlers.update_profile(session, profile_id, data, current_user.id)


@router.delete(
    "/{profile_id}",
    response_model=dtos.ProfileResponse,
    summary="Delete a profile",
)
async def delete_profile(
    profile_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the profile"),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.ProfileResponse:
    """Soft delete a profile (or hard delete if specified)."""
    return await handlers.delete_profile(
        session, profile_id, current_user.id, hard_delete
    )


# --- Profile Skills ---


@router.post(
    "/{profile_id}/skills",
    response_model=dtos.ProfileSkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a skill to a profile",
)
async def add_profile_skill(
    profile_id: int,
    data: dtos.ProfileAddSkillRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.ProfileSkillResponse:
    """Add a skill to a profile with proficiency details."""
    return await handlers.add_profile_skill(session, profile_id, data, current_user.id)


@router.put(
    "/{profile_id}/skills/{skill_id}",
    response_model=dtos.ProfileSkillResponse,
    summary="Update a profile skill",
)
async def update_profile_skill(
    profile_id: int,
    skill_id: int,
    data: dtos.ProfileUpdateSkillRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dtos.ProfileSkillResponse:
    """Update a profile skill's proficiency details."""
    return await handlers.update_profile_skill(
        session, profile_id, skill_id, data, current_user.id
    )


@router.delete(
    "/{profile_id}/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a skill from a profile",
)
async def remove_profile_skill(
    profile_id: int,
    skill_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> None:
    """Remove a skill from a profile."""
    await handlers.remove_profile_skill(session, profile_id, skill_id, current_user.id)


# --- Profile Links ---


@router.post(
    "/{profile_id}/links/{link_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Add a link to a profile",
)
async def add_profile_link(
    profile_id: int,
    link_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> shared_dtos.Message:
    """Associate a link with a profile."""
    return await handlers.add_profile_link(
        session, profile_id, link_id, current_user.id
    )


@router.delete(
    "/{profile_id}/links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a link from a profile",
)
async def remove_profile_link(
    profile_id: int,
    link_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> None:
    """Remove a link from a profile."""
    await handlers.remove_profile_link(session, profile_id, link_id, current_user.id)


# --- Profile Experiences ---


@router.post(
    "/{profile_id}/experiences/{experience_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Add an experience to a profile",
)
async def add_profile_experience(
    profile_id: int,
    experience_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> dict:
    """Associate an experience with a profile."""
    await handlers.add_profile_experience(
        session, profile_id, experience_id, current_user.id
    )
    return {"message": "Experience added to profile"}


@router.delete(
    "/{profile_id}/experiences/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an experience from a profile",
)
async def remove_profile_experience(
    profile_id: int,
    experience_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> None:
    """Remove an experience from a profile."""
    await handlers.remove_profile_experience(
        session, profile_id, experience_id, current_user.id
    )


# --- Profile Education ---


@router.post(
    "/{profile_id}/education/{education_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Add an education to a profile",
)
async def add_profile_education(
    profile_id: int,
    education_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> shared_dtos.Message:
    """Associate an education with a profile."""
    return await handlers.add_profile_education(
        session, profile_id, education_id, current_user.id
    )


@router.delete(
    "/{profile_id}/education/{education_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an education from a profile",
)
async def remove_profile_education(
    profile_id: int,
    education_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> None:
    """Remove an education from a profile."""
    await handlers.remove_profile_education(
        session, profile_id, education_id, current_user.id
    )


# --- Profile Certificates ---


@router.post(
    "/{profile_id}/certificates/{certificate_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Add a certificate to a profile",
)
async def add_profile_certificate(
    profile_id: int,
    certificate_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> shared_dtos.Message:
    """Associate a certificate with a profile."""
    return await handlers.add_profile_certificate(
        session, profile_id, certificate_id, current_user.id
    )


@router.delete(
    "/{profile_id}/certificates/{certificate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a certificate from a profile",
)
async def remove_profile_certificate(
    profile_id: int,
    certificate_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: ProfileUser = Depends(get_current_profile_user),
    _: None = Depends(_require_default_role),
) -> None:
    """Remove a certificate from a profile."""
    await handlers.remove_profile_certificate(
        session, profile_id, certificate_id, current_user.id
    )
