from src.modules.profile.features.skill import dtos
from src.modules.profile.features.skill import services
from src.modules.profile.features.skill.models import Skill
from src.shared import services as shared_services

from sqlalchemy.ext.asyncio import AsyncSession


async def create_skill(
    session: AsyncSession, data: dtos.SkillCreateRequest
) -> dtos.SkillResponse:
    """Execute the use case."""

    # Check if skill name already exists
    await shared_services.ensure_unique(
        session,
        Skill,
        "name",
        data.name,
        include_deleted=False,
        label="Skill",
    )

    # Create skill
    skill = await services.create_skill(
        session=session,
        name=data.name,
        category=data.category,
    )

    await session.refresh(skill)

    return dtos.SkillResponse.model_validate(skill)


async def delete_skill(
    session: AsyncSession, skill_id: int, hard_delete: bool = False
) -> dtos.SkillResponse:
    """Execute the use case."""

    # Find skill
    skill = await shared_services.ensure_exists(
        session, Skill, skill_id, include_deleted=True, label="Skill"
    )

    skill = await services.delete_skill(session, skill, hard_delete)

    return dtos.SkillResponse.model_validate(skill)


async def get_skill(
    session: AsyncSession, skill_id: int, include_deleted: bool = False
) -> dtos.SkillResponse:
    """Execute the use case."""

    # Find skill
    skill = await shared_services.ensure_exists(
        session, Skill, skill_id, include_deleted=include_deleted, label="Skill"
    )

    return dtos.SkillResponse.model_validate(skill)


async def list_skills(
    session: AsyncSession, filters: dtos.SkillFilterParams
) -> list[dtos.SkillResponse]:
    """Execute the use case."""

    skills = await services.get_all_skills(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        name_filter=filters.name,
        category_filter=filters.category,
        include_deleted=filters.include_deleted,
    )
    return [dtos.SkillResponse.model_validate(skill) for skill in skills]


async def update_skill(
    session: AsyncSession, skill_id: int, data: dtos.SkillUpdateRequest
) -> dtos.SkillResponse:
    """Execute the use case."""

    # Find skill
    skill = await shared_services.ensure_exists(
        session, Skill, skill_id, include_deleted=True, label="Skill"
    )

    # Check name uniqueness if changing -> TODO: essa validação deve ser feita no service de update
    if data.name and data.name != skill.name:
        await shared_services.ensure_unique(
            session,
            Skill,
            "name",
            data.name,
            include_deleted=False,
            label="Skill",
            exclude_id=skill.id,
        )

    # Update skill
    skill = await services.update_skill(
        session=session,
        skill=skill,
        name=data.name,
        category=data.category,
    )

    await session.refresh(skill)

    return dtos.SkillResponse.model_validate(skill)
