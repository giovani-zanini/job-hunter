"""Location use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.location import dtos, services
from src.modules.enterprise.features.location.models import Location
from src.shared import services as shared_services


async def create_location(
    session: AsyncSession, data: dtos.LocationCreateRequest
) -> dtos.LocationResponse:
    location = await services.create_location(session, **data.model_dump())
    await session.refresh(location)
    return dtos.LocationResponse.model_validate(location)


async def get_location(
    session: AsyncSession, location_id: int, include_deleted: bool = False
) -> dtos.LocationDetailResponse:
    location = await shared_services.ensure_exists(
        session, Location, location_id, include_deleted=include_deleted, label="Location"
    )
    return dtos.LocationDetailResponse.model_validate(location)


async def list_locations(
    session: AsyncSession, filters: dtos.LocationFilterParams
) -> list[dtos.LocationResponse]:
    locations = await services.get_all_locations(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        country_filter=filters.country,
        state_filter=filters.state,
        city_filter=filters.city,
        include_deleted=filters.include_deleted,
    )
    return [dtos.LocationResponse.model_validate(loc) for loc in locations]


async def update_location(
    session: AsyncSession, location_id: int, data: dtos.LocationUpdateRequest
) -> dtos.LocationResponse:
    location = await shared_services.ensure_exists(
        session, Location, location_id, label="Location"
    )
    location = await services.update_location(session, location, **data.model_dump(exclude_none=True))
    await session.refresh(location)
    return dtos.LocationResponse.model_validate(location)


async def delete_location(
    session: AsyncSession, location_id: int, hard_delete: bool = False
) -> dtos.LocationResponse:
    location = await shared_services.ensure_exists(
        session, Location, location_id, include_deleted=True, label="Location"
    )
    if hard_delete:
        response = dtos.LocationResponse.model_validate(location)
        await services.delete_location(session, location, hard_delete=True)
        return response
    location = await services.delete_location(session, location)
    await session.refresh(location)
    return dtos.LocationResponse.model_validate(location)
