"""Segment use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.segment import dtos, services
from src.modules.enterprise.features.segment.models import Segment
from src.shared import services as shared_services


async def create_segment(
    session: AsyncSession, data: dtos.SegmentCreateRequest
) -> dtos.SegmentResponse:
    await shared_services.ensure_unique(session, Segment, "name", data.name, label="Segment")
    segment = await services.create_segment(session, name=data.name)
    await session.refresh(segment)
    return dtos.SegmentResponse.model_validate(segment)


async def get_segment(
    session: AsyncSession, segment_id: int, include_deleted: bool = False
) -> dtos.SegmentDetailResponse:
    segment = await shared_services.ensure_exists(
        session, Segment, segment_id, include_deleted=include_deleted, label="Segment"
    )
    return dtos.SegmentDetailResponse.model_validate(segment)


async def list_segments(
    session: AsyncSession, filters: dtos.SegmentFilterParams
) -> list[dtos.SegmentResponse]:
    segments = await services.get_all_segments(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        name_filter=filters.name,
        include_deleted=filters.include_deleted,
    )
    return [dtos.SegmentResponse.model_validate(s) for s in segments]


async def update_segment(
    session: AsyncSession, segment_id: int, data: dtos.SegmentUpdateRequest
) -> dtos.SegmentResponse:
    segment = await shared_services.ensure_exists(
        session, Segment, segment_id, label="Segment"
    )
    if data.name and data.name != segment.name:
        await shared_services.ensure_unique(
            session, Segment, "name", data.name, exclude_id=segment.id, label="Segment"
        )
    segment = await services.update_segment(session, segment, name=data.name)
    await session.refresh(segment)
    return dtos.SegmentResponse.model_validate(segment)


async def delete_segment(
    session: AsyncSession, segment_id: int, hard_delete: bool = False
) -> dtos.SegmentResponse:
    segment = await shared_services.ensure_exists(
        session, Segment, segment_id, include_deleted=True, label="Segment"
    )
    if hard_delete:
        response = dtos.SegmentResponse.model_validate(segment)
        await services.delete_segment(session, segment, hard_delete=True)
        return response
    segment = await services.delete_segment(session, segment)
    await session.refresh(segment)
    return dtos.SegmentResponse.model_validate(segment)
