"""Profile use cases.

This module contains all use case functions for managing user profiles and their
associations. Use cases orchestrate calls to service layer functions and handle
transaction management (commit/rollback).

The module organizes use cases into the following groups:
    - Core Profile Operations: CRUD operations for profiles
    - Profile Skills: Managing skills associated with profiles
    - Profile Links: Managing professional links
    - Profile Experiences: Managing work experiences
    - Profile Education: Managing educational records
    - Profile Certificates: Managing professional certificates

Each use case function is responsible for:
    - Calling the appropriate service layer function(s)
    - Managing database transactions
    - Transforming models to response DTOs
    - Returning standardized responses
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.profile import dtos
from src.modules.profile.features.profile import services
from src.modules.profile.features.profile.models import Profile
from src.shared import dtos as shared_dtos
from src.shared import services as shared_services


async def create_profile(
    session: AsyncSession, user_id: int, data: dtos.ProfileCreateRequest
) -> dtos.ProfileDetailResponse:
    """Create a new user profile.

    Args:
        session: The async database session for executing queries.
        data: The profile creation request containing slug, full_name,
            title, and bio.

    Returns:
        A ProfileResponse containing the created profile data.

    Raises:
        ConflictException: If a profile with the given slug already exists.
    """
    profile = await services.create_profile(
        session=session,
        user_id=user_id,
        slug=data.slug,
        full_name=data.full_name,
        title=data.title,
        bio=data.bio,
    )

    return dtos.ProfileDetailResponse.model_validate(profile)


async def delete_profile(
    session: AsyncSession, profile_id: int, hard_delete: bool = False
) -> None:
    """Delete a user profile (soft or hard delete).

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile to delete.
        hard_delete: If True, permanently removes the profile from database.
            If False, performs a soft delete by setting deleted_at timestamp.
            Defaults to False.

    Raises:
        NotFoundException: If no profile exists with the given profile_id.
    """
    await services.delete_profile(
        session=session,
        profile_id=profile_id,
        hard_delete=hard_delete,
    )


async def get_profile(
    session: AsyncSession, profile_id: int
) -> dtos.ProfileDetailResponse:
    """Retrieve a single profile by its ID.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile to retrieve.

    Returns:
        A ProfileDetailResponse containing the complete profile data.

    Raises:
        NotFoundException: If no profile exists with the given profile_id.
    """
    profile = await services.get_profile_by_id(session, profile_id)
    return dtos.ProfileDetailResponse.model_validate(profile)


async def list_profiles(
    session: AsyncSession, filters: dtos.ProfileFilterParams
) -> list[dtos.ProfileResponse]:
    """List profiles with optional filtering and pagination.

    Args:
        session: The async database session for executing queries.
        filters: Filter parameters including skip, limit, user_id, slug,
            full_name, and include_deleted flags.

    Returns:
        A list of ProfileResponse objects matching the filter criteria.
    """
    profiles = await services.get_all_profiles(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        user_id=filters.user_id,
        slug_filter=filters.slug,
        full_name_filter=filters.full_name,
        include_deleted=filters.include_deleted,
    )
    return [dtos.ProfileResponse.model_validate(profile) for profile in profiles]


async def update_profile(
    session: AsyncSession,
    profile_id: int,
    data: dtos.ProfileUpdateRequest,
) -> dtos.ProfileResponse:
    """Update an existing user profile.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile to update.
        data: The profile update request containing optional slug, full_name,
            title, and bio fields.

    Returns:
        A ProfileResponse containing the updated profile data.

    Raises:
        NotFoundException: If no profile exists with the given profile_id.
        ConflictException: If updating slug to a value that already exists.
    """
    profile = await services.update_profile(
        session=session,
        profile_id=profile_id,
        slug=data.slug,
        full_name=data.full_name,
        title=data.title,
        bio=data.bio,
    )

    await session.refresh(profile)
    return dtos.ProfileResponse.model_validate(profile)


# --- Profile Skills Use Cases ---


async def add_profile_skill(
    session: AsyncSession,
    profile_id: int,
    data: dtos.ProfileAddSkillRequest,
) -> dtos.ProfileSkillResponse:
    """Add a skill to a user profile with proficiency details.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile.
        data: The skill addition request containing skill_id, level,
            years_of_experience, and last_used_at.

    Returns:
        A ProfileSkillResponse containing the created profile-skill association.

    Raises:
        NotFoundException: If profile_id or skill_id does not exist.
        ConflictException: If the skill is already associated with this profile.
    """
    profile_skill = await services.add_profile_skill(
        session,
        profile_id,
        data.skill_id,
        data.level,
        data.years_of_experience,
        data.last_used_at,
    )

    await session.refresh(profile_skill)

    return dtos.ProfileSkillResponse.model_validate(profile_skill)


async def update_profile_skill(
    session: AsyncSession,
    profile_id: int,
    skill_id: int,
    data: dtos.ProfileUpdateSkillRequest,
) -> dtos.ProfileSkillResponse:
    """Update proficiency details for a skill associated with a profile.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile.
        skill_id: The unique identifier of the skill to update.
        data: The skill update request containing optional level,
            years_of_experience, and last_used_at fields.

    Returns:
        A ProfileSkillResponse containing the updated profile-skill association.

    Raises:
        NotFoundException: If the profile-skill association does not exist.
    """
    profile_skill = await services.update_profile_skill(
        session,
        profile_id,
        skill_id,
        data.level,
        data.years_of_experience,
        data.last_used_at,
    )

    await session.refresh(profile_skill)
    return dtos.ProfileSkillResponse.model_validate(profile_skill)


async def remove_profile_skill(
    session: AsyncSession, profile_id: int, skill_id: int,
) -> None:
    """Remove a skill association from a user profile.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile.
        skill_id: The unique identifier of the skill to remove.

    Raises:
        NotFoundException: If the profile-skill association does not exist.
    """
    await services.remove_profile_skill(session, profile_id, skill_id)


# --- Profile Links Use Cases ---


async def add_profile_link(
    session: AsyncSession, profile_id: int, link_id: int,
) -> shared_dtos.Message:
    """Associate a professional link with a user profile.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile.
        link_id: The unique identifier of the link to associate.

    Returns:
        A Message containing confirmation and metadata with link_id and profile_id.

    Raises:
        NotFoundException: If profile_id or link_id does not exist.
        ConflictException: If the link is already associated with this profile.
    """
    await services.add_profile_link(session, profile_id, link_id)

    return shared_dtos.Message(
        message="Link added to profile.",
        meta={"link_id": link_id, "profile_id": profile_id},
    )


async def remove_profile_link(
    session: AsyncSession, profile_id: int, link_id: int,
) -> None:
    """Remove a professional link association from a user profile.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile.
        link_id: The unique identifier of the link to remove.

    Raises:
        NotFoundException: If the profile-link association does not exist.
    """
    await services.remove_profile_link(session, profile_id, link_id)


# --- Profile Experiences Use Cases ---


async def add_profile_experience(
    session: AsyncSession, profile_id: int, experience_id: int,
) -> None:
    """Associate a work experience with a user profile.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile.
        experience_id: The unique identifier of the experience to associate.

    Raises:
        NotFoundException: If profile_id or experience_id does not exist.
        ConflictException: If the experience is already associated with this profile.
    """
    await services.add_profile_experience(session, profile_id, experience_id)


async def remove_profile_experience(
    session: AsyncSession, profile_id: int, experience_id: int,
) -> None:
    """Remove a work experience association from a user profile.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile.
        experience_id: The unique identifier of the experience to remove.

    Raises:
        NotFoundException: If the profile-experience association does not exist.
    """
    await services.remove_profile_experience(session, profile_id, experience_id)


# --- Profile Education Use Cases ---


async def add_profile_education(
    session: AsyncSession, profile_id: int, education_id: int,
) -> shared_dtos.Message:
    """Associate an educational record with a user profile.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile.
        education_id: The unique identifier of the education record to associate.

    Returns:
        A Message containing confirmation and metadata with education_id and profile_id.

    Raises:
        NotFoundException: If profile_id or education_id does not exist.
        ConflictException: If the education is already associated with this profile.
    """
    await services.add_profile_education(session, profile_id, education_id)

    return shared_dtos.Message(
        message="Education added to profile.",
        meta={"education_id": education_id, "profile_id": profile_id},
    )


async def remove_profile_education(
    session: AsyncSession, profile_id: int, education_id: int,
) -> None:
    """Remove an educational record association from a user profile.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile.
        education_id: The unique identifier of the education record to remove.

    Raises:
        NotFoundException: If the profile-education association does not exist.
    """
    await services.remove_profile_education(session, profile_id, education_id)


# --- Profile Certificates Use Cases ---


async def add_profile_certificate(
    session: AsyncSession, profile_id: int, certificate_id: int,
) -> shared_dtos.Message:
    """Associate a professional certificate with a user profile.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile.
        certificate_id: The unique identifier of the certificate to associate.

    Returns:
        A Message containing confirmation and metadata with certificate_id and profile_id.

    Raises:
        NotFoundException: If profile_id or certificate_id does not exist.
        ConflictException: If the certificate is already associated with this profile.
    """
    await services.add_profile_certificate(session, profile_id, certificate_id)

    return shared_dtos.Message(
        message="Certificate added to profile.",
        meta={"certificate_id": certificate_id, "profile_id": profile_id},
    )


async def remove_profile_certificate(
    session: AsyncSession, profile_id: int, certificate_id: int,
) -> None:
    """Remove a professional certificate association from a user profile.

    Args:
        session: The async database session for executing queries.
        profile_id: The unique identifier of the profile.
        certificate_id: The unique identifier of the certificate to remove.

    Raises:
        NotFoundException: If the profile-certificate association does not exist.
    """
    await services.remove_profile_certificate(session, profile_id, certificate_id)
