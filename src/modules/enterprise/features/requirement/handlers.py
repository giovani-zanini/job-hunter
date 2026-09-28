"""Requirement use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.requirement import dtos, services
from src.modules.enterprise.features.requirement.models import Requirement
from src.shared import services as shared_services


async def create_requirement(
    session: AsyncSession, data: dtos.RequirementCreateRequest
) -> dtos.RequirementResponse:
    requirement = await services.create_requirement(session, skill=data.skill)
    await session.refresh(requirement)
    return dtos.RequirementResponse.model_validate(requirement)


async def get_requirement(
    session: AsyncSession, requirement_id: int, include_deleted: bool = False
) -> dtos.RequirementDetailResponse:
    requirement = await shared_services.ensure_exists(
        session, Requirement, requirement_id, include_deleted=include_deleted, label="Requirement"
    )
    return dtos.RequirementDetailResponse.model_validate(requirement)


async def list_requirements(
    session: AsyncSession, filters: dtos.RequirementFilterParams
) -> list[dtos.RequirementResponse]:
    requirements = await services.get_all_requirements(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        skill_filter=filters.skill,
        include_deleted=filters.include_deleted,
    )
    return [dtos.RequirementResponse.model_validate(r) for r in requirements]


async def update_requirement(
    session: AsyncSession, requirement_id: int, data: dtos.RequirementUpdateRequest
) -> dtos.RequirementResponse:
    requirement = await shared_services.ensure_exists(
        session, Requirement, requirement_id, label="Requirement"
    )
    requirement = await services.update_requirement(session, requirement, skill=data.skill)
    await session.refresh(requirement)
    return dtos.RequirementResponse.model_validate(requirement)


async def delete_requirement(
    session: AsyncSession, requirement_id: int, hard_delete: bool = False
) -> dtos.RequirementResponse:
    requirement = await shared_services.ensure_exists(
        session, Requirement, requirement_id, include_deleted=True, label="Requirement"
    )
    if hard_delete:
        response = dtos.RequirementResponse.model_validate(requirement)
        await services.delete_requirement(session, requirement, hard_delete=True)
        return response
    requirement = await services.delete_requirement(session, requirement)
    await session.refresh(requirement)
    return dtos.RequirementResponse.model_validate(requirement)
