"""Use cases for experience feature."""

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.experience import dtos
from src.modules.profile.features.experience import services
from src.modules.profile.features.experience.models import (
    Experience,
    Achievements,
    ExperienceSkills,
)
from src.modules.profile.features.company.models import Company
from src.modules.profile.features.skill.models import Skill
from src.modules.profile.features.skill.services import ensure_skills_exist
from src.shared import exceptions
from src.shared import services as shared_services
from src.shared import dtos as shared_dtos


async def create_experience(
    session: AsyncSession, user_id: int, data: dtos.ExperienceCreateRequest
) -> dtos.ExperienceDetailResponse:
    """
    Create a new experience.

    Orchestrates:
    1. Validate company exists
    2. Validate skills exist
    3. Create experience with achievements and skills
    """
    # Validate company exists
    await shared_services.ensure_exists(
        session, Company, data.company_id, label="Company"
    )

    # Validate skills exist
    await ensure_skills_exist(session, data.skill_ids)

    # Create experience
    experience = await services.create_experience(
        session,
        user_id=user_id,
        company_id=data.company_id,
        position_title=data.position_title,
        start_date=data.start_date,
        end_date=data.end_date,
        description=data.description,
    )

    # Add achievements
    for achievement_data in data.achievements:
        await services.add_achievement(
            session,
            experience_id=experience.id,
            title=achievement_data.title,
            description=achievement_data.description,
        )

    # Add skills
    for skill_id in data.skill_ids:
        await services.add_experience_skill(session, experience.id, skill_id)

    # Reload with associations
    experience = await services.get_experience_by_id(
        session, experience.id, load_achievements=True
    )

    return dtos.ExperienceDetailResponse.model_validate(experience)


async def get_experience(
    session: AsyncSession, experience_id: int, include_deleted: bool = False
) -> dtos.ExperienceDetailResponse:
    """Get an experience by ID."""
    await shared_services.ensure_exists(
        session,
        Experience,
        experience_id,
        include_deleted=include_deleted,
        label="Experience",
    )
    experience = await services.get_experience_by_id(
        session, experience_id, include_deleted=include_deleted, load_achievements=True
    )

    return dtos.ExperienceDetailResponse.model_validate(experience)


async def list_experiences(
    session: AsyncSession, filters: dtos.ExperienceFilterParams
) -> List[dtos.ExperienceResponse]:
    """List experiences with filters."""
    experiences = await services.get_all_experiences(
        session,
        skip=filters.skip,
        limit=filters.limit,
        user_id=filters.user_id,
        company_id=filters.company_id,
        position_title_filter=filters.position_title,
        include_deleted=filters.include_deleted,
    )

    return [dtos.ExperienceResponse.model_validate(exp) for exp in experiences]


async def update_experience(
    session: AsyncSession,
    experience_id: int,
    data: dtos.ExperienceUpdateRequest,
    user_id: int,
) -> dtos.ExperienceResponse:
    """
    Update an experience.

    Orchestrates:
    1. Find experience by ID
    2. Validate company exists if changing
    3. Update experience fields
    """
    # Find experience
    experience = await shared_services.ensure_exists(
        session, Experience, experience_id, label="Experience"
    )

    if experience.user_id != user_id:
        raise exceptions.ForbiddenException(
            detail="Not authorized to update this experience."
        )

    # Validate company exists if changing
    if data.company_id and data.company_id != experience.company_id:
        await shared_services.ensure_exists(
            session, Company, data.company_id, label="Company"
        )

    # Update experience
    experience = await services.update_experience(
        session,
        experience=experience,
        company_id=data.company_id,
        position_title=data.position_title,
        start_date=data.start_date,
        end_date=data.end_date,
        description=data.description,
    )

    await session.refresh(experience)

    return dtos.ExperienceResponse.model_validate(experience)


async def delete_experience(
    session: AsyncSession, experience_id: int, user_id: int, hard_delete: bool = False
) -> dtos.ExperienceResponse:
    """
    Delete an experience (soft or hard delete).

    Orchestrates:
    1. Find experience by ID
    2. Soft or hard delete experience
    """
    experience = await shared_services.ensure_exists(
        session, Experience, experience_id, include_deleted=True, label="Experience"
    )

    if experience.user_id != user_id:
        raise exceptions.ForbiddenException(
            detail="Not authorized to delete this experience."
        )

    if hard_delete:
        response = dtos.ExperienceResponse.model_validate(experience)
        await services.delete_experience(session, experience, hard_delete=True)

        return response

    experience = await services.delete_experience(session, experience)

    await session.refresh(experience)

    return dtos.ExperienceResponse.model_validate(experience)


# --- Achievement Use Cases ---


async def add_achievement(
    session: AsyncSession, experience_id: int, data: dtos.AchievementInput
) -> dtos.AchievementResponse:
    """Add an achievement to an experience."""
    # Validate experience exists
    await shared_services.ensure_exists(
        session, Experience, experience_id, label="Experience"
    )

    # Create achievement
    achievement = await services.add_achievement(
        session,
        experience_id=experience_id,
        title=data.title,
        description=data.description,
    )

    await session.refresh(achievement)

    return dtos.AchievementResponse.model_validate(achievement)


async def update_achievement(
    session: AsyncSession, achievement_id: int, data: dtos.AchievementUpdateRequest
) -> dtos.AchievementResponse:
    """Update an achievement."""
    # Find achievement
    achievement = await shared_services.ensure_exists(
        session, Achievements, achievement_id, include_deleted=True, label="Achievement"
    )

    # Update achievement
    achievement = await services.update_achievement(
        session, achievement=achievement, title=data.title, description=data.description
    )

    await session.refresh(achievement)

    return dtos.AchievementResponse.model_validate(achievement)


async def remove_achievement(session: AsyncSession, achievement_id: int) -> None:
    """Remove an achievement."""
    # Find achievement
    achievement = await shared_services.ensure_exists(
        session, Achievements, achievement_id, include_deleted=True, label="Achievement"
    )

    # Remove achievement
    await services.remove_achievement(session, achievement)


# --- Experience Skill Use Cases ---


async def add_experience_skill(
    session: AsyncSession, experience_id: int, skill_id: int
) -> shared_dtos.Message:
    """Add a skill to an experience."""
    # Validate experience exists
    await shared_services.ensure_exists(
        session, Experience, experience_id, label="Experience"
    )

    # Validate skill exists
    await shared_services.ensure_exists(session, Skill, skill_id, label="Skill")

    # Check if association already exists
    await shared_services.ensure_association(
        session,
        ExperienceSkills,
        shared_dtos.Association(
            left_field_name="experience_id",
            left_field_value=experience_id,
            right_field_name="skill_id",
            right_field_value=skill_id,
            left_label="Experience",
            right_label="Skill",
        ),
        type="absent",
    )

    # Create association
    await services.add_experience_skill(session, experience_id, skill_id)

    return shared_dtos.Message(
        message="Skill added to experience.",
        meta={"skill_id": skill_id, "experience_id": experience_id},
    )


async def remove_experience_skill(
    session: AsyncSession, experience_id: int, skill_id: int
) -> None:
    """Remove a skill from an experience."""
    # Find association
    exp_skill = await shared_services.ensure_association(
        session,
        ExperienceSkills,
        shared_dtos.Association(
            left_field_name="experience_id",
            left_field_value=experience_id,
            right_field_name="skill_id",
            right_field_value=skill_id,
            left_label="Experience",
            right_label="Skill",
        ),
        type="present",
    )

    # Remove association
    await services.remove_experience_skill(session, exp_skill)
