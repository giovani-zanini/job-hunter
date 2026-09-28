"""Segment service — database operations."""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.segment.models import Segment
from src.shared import services as shared_services


async def get_all_segments(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    name_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[Segment]:
    stmt = select(Segment)
    if not include_deleted:
        stmt = stmt.where(Segment.deleted_at.is_(None))
    if name_filter:
        stmt = stmt.where(Segment.name.ilike(f"%{name_filter}%"))
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_segment(session: AsyncSession, name: str) -> Segment:
    return await shared_services.create(session, Segment, name=name)


async def update_segment(
    session: AsyncSession, segment: Segment, name: Optional[str] = None
) -> Segment:
    if name is not None:
        segment.name = name
    await session.flush()
    return segment


async def delete_segment(
    session: AsyncSession, segment: Segment, hard_delete: bool = False
) -> Segment:
    return await shared_services.delete(session, segment, hard_delete)
