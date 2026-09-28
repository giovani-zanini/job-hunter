"""Profile service for database operations.

This module provides service layer functions for managing user profiles and their
associations with skills, links, experiences, education records, and certificates.
All operations are performed asynchronously using SQLAlchemy AsyncSession.

The service handles:
    - CRUD operations for profiles
    - Profile associations with skills (with level and experience tracking)
    - Profile associations with links, experiences, education, and certificates
    - Validation of entity existence and uniqueness constraints
    - Soft and hard deletion support
"""

from datetime import date
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.skill.models import Skill
from src.modules.profile.features.user.models import User
from src.modules.profile.features.profile.models import Profile, ProfileSkills
from src.modules.profile.features.link.models import Link, ProfileLink
from src.modules.profile.features.experience.models import Experience, ProfileExperience
from src.modules.profile.features.education.models import Education, ProfileEducation
from src.modules.profile.features.certificate.models import (
    Certificate,
    ProfileCertificate,
)
from src.shared import services as shared_services
from src.shared import dtos as shared_dtos


async def get_profile_by_id(
    session: AsyncSession,
    profile_id: int,
) -> Optional[Profile]:
    """Get a profile by ID.

    Args:
        session: The database session for executing queries.
        profile_id: The unique identifier of the profile to retrieve.

    Returns:
        The profile instance if found.

    Raises:
        EntityNotFound: If no profile exists with the given ID.
    """
    profile = await shared_services.get_one_by_field(
        session=session,
        model=Profile,
        field_name="id",
        field_value=profile_id,
        raise_not_found_exception=True,
    )
    return profile


async def get_all_profiles(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[int] = None,
    slug_filter: Optional[str] = None,
    full_name_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[Profile]:
    """Get all profiles with optional filters and pagination.

    Args:
        session: The database session for executing queries.
        skip: Number of records to skip for pagination. Defaults to 0.
        limit: Maximum number of records to return. Defaults to 20.
        user_id: Filter profiles by user ID if provided.
        slug_filter: Case-insensitive partial match filter for profile slug.
        full_name_filter: Case-insensitive partial match filter for full name.
        include_deleted: Whether to include soft-deleted profiles. Defaults to False.

    Returns:
        A sequence of profile instances matching the filters.
    """
    stmt = select(Profile)

    if not include_deleted:
        stmt = stmt.where(Profile.deleted_at.is_(None))

    if user_id:
        stmt = stmt.where(Profile.user_id == user_id)

    if slug_filter:
        stmt = stmt.where(Profile.slug.ilike(f"%{slug_filter}%"))

    if full_name_filter:
        stmt = stmt.where(Profile.full_name.ilike(f"%{full_name_filter}%"))

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_profile(
    session: AsyncSession,
    user_id: int,
    slug: str,
    full_name: str,
    title: str,
    bio: str,
) -> Profile:
    """Create a new profile.

    Args:
        session: The database session for executing queries.
        user_id: The ID of the user who owns this profile.
        slug: A unique URL-friendly identifier for the profile.
        full_name: The full name of the profile owner.
        title: The professional title or headline.
        bio: The biography or description text.

    Returns:
        The newly created profile instance.

    Raises:
        EntityNotFound: If the user with the given user_id does not exist.
        UniqueConstraintError: If a profile with the given slug already exists.
    """
    # Validate user exists
    await shared_services.get_one_by_field(
        session=session,
        model=User,
        field_name="id",
        field_value=user_id,
        raise_not_found_exception=True,
    )

    # Validate slug is unique
    await shared_services.ensure_unique(
        session=session,
        model=Profile,
        field_name="slug",
        value=slug,
        include_deleted=True,
        label="Profile",
    )

    # Create profile
    profile = await shared_services.create(
        session=session,
        model=Profile,
        user_id=user_id,
        slug=slug,
        full_name=full_name,
        title=title,
        bio=bio,
    )

    return profile


async def update_profile(
    session: AsyncSession,
    profile_id: int,
    slug: Optional[str] = None,
    full_name: Optional[str] = None,
    title: Optional[str] = None,
    bio: Optional[str] = None,
) -> Profile:
    """Update profile fields.

    Only provided fields will be updated. Fields set to None are ignored.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile to update.
        slug: New slug value. Must be unique if provided.
        full_name: New full name value.
        title: New title value.
        bio: New bio value.

    Returns:
        The updated profile instance.

    Raises:
        EntityNotFound: If no profile exists with the given profile_id.
        UniqueConstraintError: If the new slug already exists for another profile.
    """
    # Find profile
    profile = await shared_services.get_one_by_field(
        session=session,
        model=Profile,
        field_name="id",
        field_value=profile_id,
        raise_not_found_exception=True,
    )

    if slug is not None and slug != profile.slug:
        await shared_services.ensure_unique(
            session=session,
            model=Profile,
            field_name="slug",
            value=slug,
            include_deleted=True,
            label="Profile",
            exclude_id=profile.id,
        )
        profile.slug = slug

    if full_name is not None:
        profile.full_name = full_name

    if title is not None:
        profile.title = title

    if bio is not None:
        profile.bio = bio

    await session.flush()
    return profile


async def delete_profile(
    session: AsyncSession, profile_id: int, hard_delete: bool = False
) -> None:
    """Delete a profile (soft or hard delete).

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile to delete.
        hard_delete: If True, permanently removes the record from database.
            If False, performs a soft delete by setting deleted_at timestamp.
            Defaults to False.

    Raises:
        EntityNotFound: If no profile exists with the given profile_id.
    """
    profile = await shared_services.get_one_by_field(
        session=session,
        model=Profile,
        field_name="id",
        field_value=profile_id,
        include_deleted=True,
        raise_not_found_exception=True,
    )
    await shared_services.delete(session, profile, hard_delete=hard_delete)


# --- Skill Association Functions ---


async def add_profile_skill(
    session: AsyncSession,
    profile_id: int,
    skill_id: int,
    level: int,
    years_of_experience: int,
    last_used_at: Optional[date] = None,
) -> ProfileSkills:
    """Add a skill to a profile with proficiency details.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile.
        skill_id: The ID of the skill to associate.
        level: The proficiency level for this skill.
        years_of_experience: Number of years of experience with this skill.
        last_used_at: The date when this skill was last used. Optional.

    Returns:
        The created ProfileSkills association instance.

    Raises:
        EntityNotFound: If the profile or skill does not exist.
        AssociationAlreadyExists: If this skill is already associated with the profile.
    """
    # Validate profile exists
    await shared_services.get_one_by_field(
        session=session,
        model=Profile,
        field_name="id",
        field_value=profile_id,
        raise_not_found_exception=True,
    )

    # Validate skill exists
    await shared_services.get_one_by_field(
        session=session,
        model=Skill,
        field_name="id",
        field_value=skill_id,
        raise_not_found_exception=True,
    )

    # Check if association already exists
    await shared_services.ensure_association(
        session=session,
        model=ProfileSkills,
        config=shared_dtos.Association(
            left_field_name="profile_id",
            left_field_value=profile_id,
            right_field_name="skill_id",
            right_field_value=skill_id,
            left_label="Profile",
            right_label="Skill",
        ),
        type="absent",
    )

    return await shared_services.create(
        session,
        ProfileSkills,
        profile_id=profile_id,
        skill_id=skill_id,
        level=level,
        years_of_experience=years_of_experience,
        last_used_at=last_used_at,
    )


async def update_profile_skill(
    session: AsyncSession,
    profile_id: int,
    skill_id: int,
    level: int | None = None,
    years_of_experience: int | None = None,
    last_used_at: date | None = None,
) -> ProfileSkills:
    """Update proficiency details of a skill associated with a profile.

    Only provided fields will be updated. Fields set to None are ignored.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile.
        skill_id: The ID of the associated skill.
        level: New proficiency level value.
        years_of_experience: New years of experience value.
        last_used_at: New last used date value.

    Returns:
        The updated ProfileSkills association instance.

    Raises:
        AssociationNotFound: If the skill is not associated with the profile.
    """
    profile_skill = await shared_services.ensure_association(
        session=session,
        model=ProfileSkills,
        config=shared_dtos.Association(
            left_field_name="profile_id",
            left_field_value=profile_id,
            right_field_name="skill_id",
            right_field_value=skill_id,
            left_label="Profile",
            right_label="Skill",
        ),
        type="present",
    )

    if level is not None:
        profile_skill.level = level

    if years_of_experience is not None:
        profile_skill.years_of_experience = years_of_experience

    if last_used_at is not None:
        profile_skill.last_used_at = last_used_at

    return profile_skill


async def remove_profile_skill(
    session: AsyncSession,
    profile_id: int,
    skill_id: int,
) -> None:
    """Remove a skill association from a profile.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile.
        skill_id: The ID of the skill to disassociate.

    Raises:
        AssociationNotFound: If the skill is not associated with the profile.
    """
    profile_skill = await shared_services.ensure_association(
        session=session,
        model=ProfileSkills,
        config=shared_dtos.Association(
            left_field_name="profile_id",
            left_field_value=profile_id,
            right_field_name="skill_id",
            right_field_value=skill_id,
            left_label="Profile",
            right_label="Skill",
        ),
        type="present",
    )
    await shared_services.delete(session, profile_skill)


# --- Link Association Functions ---


async def add_profile_link(
    session: AsyncSession, profile_id: int, link_id: int
) -> ProfileLink:
    """Add a link association to a profile.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile.
        link_id: The ID of the link to associate.

    Returns:
        The created ProfileLink association instance.

    Raises:
        EntityNotFound: If the profile or link does not exist.
        AssociationAlreadyExists: If this link is already associated with the profile.
    """
    # Validate profile exists
    await shared_services.ensure_exists(session, Profile, profile_id, label="Profile")

    # Validate link exists
    await shared_services.ensure_exists(session, Link, link_id, label="Link")

    # Check if association already exists
    await shared_services.ensure_association(
        session=session,
        model=ProfileLink,
        config=shared_dtos.Association(
            left_field_name="profile_id",
            left_field_value=profile_id,
            right_field_name="link_id",
            right_field_value=link_id,
            left_label="Profile",
            right_label="Link",
        ),
        type="absent",
    )
    return await shared_services.create(
        session,
        ProfileLink,
        profile_id=profile_id,
        link_id=link_id,
    )


async def remove_profile_link(
    session: AsyncSession,
    profile_id: int,
    link_id: int,
) -> None:
    """Remove a link association from a profile.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile.
        link_id: The ID of the link to disassociate.

    Raises:
        AssociationNotFound: If the link is not associated with the profile.
    """
    # Find association
    profile_link = await shared_services.ensure_association(
        session=session,
        model=ProfileLink,
        config=shared_dtos.Association(
            left_field_name="profile_id",
            left_field_value=profile_id,
            right_field_name="link_id",
            right_field_value=link_id,
            left_label="Profile",
            right_label="Link",
        ),
        type="present",
    )
    await shared_services.delete(session, profile_link)


# --- Experience Association Functions ---


async def add_profile_experience(
    session: AsyncSession, profile_id: int, experience_id: int
) -> ProfileExperience:
    """Add an experience association to a profile.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile.
        experience_id: The ID of the experience to associate.

    Returns:
        The created ProfileExperience association instance.

    Raises:
        EntityNotFound: If the profile or experience does not exist.
        AssociationAlreadyExists: If this experience is already associated with the profile.
    """
    # Validate profile exists
    await shared_services.ensure_exists(
        session=session,
        model=Profile,
        id=profile_id,
        label="Profile",
    )

    # Validate experience exists
    await shared_services.ensure_exists(
        session=session,
        model=Experience,
        id=experience_id,
        label="Experience",
    )

    # Check if association already exists
    await shared_services.ensure_association(
        session=session,
        model=ProfileExperience,
        config=shared_dtos.Association(
            left_field_name="profile_id",
            left_field_value=profile_id,
            right_field_name="experience_id",
            right_field_value=experience_id,
            left_label="Profile",
            right_label="Experience",
        ),
        type="absent",
    )
    return await shared_services.create(
        session=session,
        model=ProfileExperience,
        profile_id=profile_id,
        experience_id=experience_id,
    )


async def remove_profile_experience(
    session: AsyncSession, profile_id: int, experience_id: int
) -> None:
    """Remove an experience association from a profile.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile.
        experience_id: The ID of the experience to disassociate.

    Raises:
        AssociationNotFound: If the experience is not associated with the profile.
    """
    # Find association
    profile_exp = await shared_services.ensure_association(
        session=session,
        model=ProfileExperience,
        config=shared_dtos.Association(
            left_field_name="profile_id",
            left_field_value=profile_id,
            right_field_name="experience_id",
            right_field_value=experience_id,
            left_label="Profile",
            right_label="Experience",
        ),
        type="present",
    )
    await shared_services.delete(session, profile_exp)


# --- Education Association Functions ---


async def add_profile_education(
    session: AsyncSession, profile_id: int, education_id: int
) -> ProfileEducation:
    """Add an education association to a profile.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile.
        education_id: The ID of the education to associate.

    Returns:
        The created ProfileEducation association instance.

    Raises:
        EntityNotFound: If the profile or education does not exist.
        AssociationAlreadyExists: If this education is already associated with the profile.
    """
    # Validate profile exists
    await shared_services.ensure_exists(session, Profile, profile_id, label="Profile")

    # Validate education exists
    await shared_services.ensure_exists(
        session, Education, education_id, label="Education"
    )

    # Check if association already exists
    await shared_services.ensure_association(
        session=session,
        model=ProfileEducation,
        config=shared_dtos.Association(
            left_field_name="profile_id",
            left_field_value=profile_id,
            right_field_name="education_id",
            right_field_value=education_id,
            left_label="Profile",
            right_label="Education",
        ),
        type="absent",
    )
    return await shared_services.create(
        session=session,
        model=ProfileEducation,
        profile_id=profile_id,
        education_id=education_id,
    )


async def remove_profile_education(
    session: AsyncSession, profile_id: int, education_id: int
) -> None:
    """Remove an education association from a profile.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile.
        education_id: The ID of the education to disassociate.

    Raises:
        AssociationNotFound: If the education is not associated with the profile.
    """
    # Find association
    profile_edu = await shared_services.ensure_association(
        session=session,
        model=ProfileEducation,
        config=shared_dtos.Association(
            left_field_name="profile_id",
            left_field_value=profile_id,
            right_field_name="education_id",
            right_field_value=education_id,
            left_label="Profile",
            right_label="Education",
        ),
        type="present",
    )
    await shared_services.delete(session, profile_edu)


# --- Certificate Association Functions ---


async def add_profile_certificate(
    session: AsyncSession, profile_id: int, certificate_id: int
) -> ProfileCertificate:
    """Add a certificate association to a profile.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile.
        certificate_id: The ID of the certificate to associate.

    Returns:
        The created ProfileCertificate association instance.

    Raises:
        EntityNotFound: If the profile or certificate does not exist.
        AssociationAlreadyExists: If this certificate is already associated with the profile.
    """
    # Validate profile exists
    await shared_services.ensure_exists(
        session=session,
        model=Profile,
        entity_id=profile_id,
        label="Profile",
    )

    # Validate certificate exists
    await shared_services.ensure_exists(
        session=session,
        model=Certificate,
        entity_id=certificate_id,
        label="Certificate",
    )

    # Check if association already exists
    await shared_services.ensure_association(
        session=session,
        model=ProfileCertificate,
        config=shared_dtos.Association(
            left_field_name="profile_id",
            left_field_value=profile_id,
            right_field_name="certificate_id",
            right_field_value=certificate_id,
            left_label="Profile",
            right_label="Certificate",
        ),
        type="absent",
    )
    return await shared_services.create(
        session=session,
        model=ProfileCertificate,
        profile_id=profile_id,
        certificate_id=certificate_id,
    )


async def remove_profile_certificate(
    session: AsyncSession, profile_id: int, certificate_id: int
) -> None:
    """Remove a certificate association from a profile.

    Args:
        session: The database session for executing queries.
        profile_id: The ID of the profile.
        certificate_id: The ID of the certificate to disassociate.

    Raises:
        AssociationNotFound: If the certificate is not associated with the profile.
    """
    # Find association
    profile_cert = await shared_services.ensure_association(
        session=session,
        model=ProfileCertificate,
        config=shared_dtos.Association(
            left_field_name="profile_id",
            left_field_value=profile_id,
            right_field_name="certificate_id",
            right_field_value=certificate_id,
            left_label="Profile",
            right_label="Certificate",
        ),
        type="present",
    )
    await shared_services.delete(session, profile_cert)
