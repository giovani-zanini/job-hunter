"""Responsability use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.responsability import dtos, services
from src.modules.enterprise.features.responsability.models import Responsability
from src.shared import services as shared_services


async def create_responsability(
    session: AsyncSession, data: dtos.ResponsabilityCreateRequest
) -> dtos.ResponsabilityResponse:
    responsability = await services.create_responsability(
        session, action=data.action, target=data.target, outcome=data.outcome
    )
    await session.refresh(responsability)
    return dtos.ResponsabilityResponse.model_validate(responsability)


async def get_responsability(
    session: AsyncSession, responsability_id: int, include_deleted: bool = False
) -> dtos.ResponsabilityDetailResponse:
    responsability = await shared_services.ensure_exists(
        session, Responsability, responsability_id, include_deleted=include_deleted, label="Responsability"
    )
    return dtos.ResponsabilityDetailResponse.model_validate(responsability)


async def list_responsabilities(
    session: AsyncSession, filters: dtos.ResponsabilityFilterParams
) -> list[dtos.ResponsabilityResponse]:
    responsabilities = await services.get_all_responsabilities(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        action_filter=filters.action,
        include_deleted=filters.include_deleted,
    )
    return [dtos.ResponsabilityResponse.model_validate(r) for r in responsabilities]


async def update_responsability(
    session: AsyncSession, responsability_id: int, data: dtos.ResponsabilityUpdateRequest
) -> dtos.ResponsabilityResponse:
    responsability = await shared_services.ensure_exists(
        session, Responsability, responsability_id, label="Responsability"
    )
    responsability = await services.update_responsability(
        session, responsability, action=data.action, target=data.target, outcome=data.outcome
    )
    await session.refresh(responsability)
    return dtos.ResponsabilityResponse.model_validate(responsability)


async def delete_responsability(
    session: AsyncSession, responsability_id: int, hard_delete: bool = False
) -> dtos.ResponsabilityResponse:
    responsability = await shared_services.ensure_exists(
        session, Responsability, responsability_id, include_deleted=True, label="Responsability"
    )
    if hard_delete:
        response = dtos.ResponsabilityResponse.model_validate(responsability)
        await services.delete_responsability(session, responsability, hard_delete=True)
        return response
    responsability = await services.delete_responsability(session, responsability)
    await session.refresh(responsability)
    return dtos.ResponsabilityResponse.model_validate(responsability)
