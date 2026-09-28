"""Location service — database operations."""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.location.models import Location
from src.shared import services as shared_services


async def get_all_locations(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    country_filter: Optional[str] = None,
    state_filter: Optional[str] = None,
    city_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[Location]:
    stmt = select(Location)
    if not include_deleted:
        stmt = stmt.where(Location.deleted_at.is_(None))
    if country_filter:
        stmt = stmt.where(Location.country.ilike(f"%{country_filter}%"))
    if state_filter:
        stmt = stmt.where(Location.state.ilike(f"%{state_filter}%"))
    if city_filter:
        stmt = stmt.where(Location.city.ilike(f"%{city_filter}%"))
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_location(session: AsyncSession, **fields) -> Location:
    return await shared_services.create(session, Location, **fields)


async def update_location(
    session: AsyncSession,
    location: Location,
    country: Optional[str] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    neighborhood: Optional[str] = None,
    postal_code: Optional[str] = None,
    street: Optional[str] = None,
    number: Optional[str] = None,
    complement: Optional[str] = None,
) -> Location:
    if country is not None:
        location.country = country
    if state is not None:
        location.state = state
    if city is not None:
        location.city = city
    if neighborhood is not None:
        location.neighborhood = neighborhood
    if postal_code is not None:
        location.postal_code = postal_code
    if street is not None:
        location.street = street
    if number is not None:
        location.number = number
    if complement is not None:
        location.complement = complement
    await session.flush()
    return location


async def delete_location(
    session: AsyncSession, location: Location, hard_delete: bool = False
) -> Location:
    return await shared_services.delete(session, location, hard_delete)
