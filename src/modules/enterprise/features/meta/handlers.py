"""Meta use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.meta import dtos, services
from src.modules.enterprise.features.meta.models import Meta
from src.shared import services as shared_services


async def create_meta(
    session: AsyncSession, data: dtos.MetaCreateRequest
) -> dtos.MetaResponse:
    meta = await services.create_meta(
        session,
        app_version=data.app_version,
        extraction_timestamp=data.extraction_timestamp,
        parsing_timestamp=data.parsing_timestamp,
        source_url=data.source_url,
        custom_data=data.custom_data,
        vacancy_id=data.vacancy_id,
        company_id=data.company_id,
    )
    await session.refresh(meta)
    return dtos.MetaResponse.model_validate(meta)


async def get_meta(
    session: AsyncSession, meta_id: int, include_deleted: bool = False
) -> dtos.MetaDetailResponse:
    meta = await shared_services.ensure_exists(
        session, Meta, meta_id, include_deleted=include_deleted, label="Meta"
    )
    return dtos.MetaDetailResponse.model_validate(meta)


async def list_metas(
    session: AsyncSession, filters: dtos.MetaFilterParams
) -> list[dtos.MetaResponse]:
    metas = await services.get_all_metas(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        vacancy_id_filter=filters.vacancy_id,
        company_id_filter=filters.company_id,
        include_deleted=filters.include_deleted,
    )
    return [dtos.MetaResponse.model_validate(m) for m in metas]


async def update_meta(
    session: AsyncSession, meta_id: int, data: dtos.MetaUpdateRequest
) -> dtos.MetaResponse:
    meta = await shared_services.ensure_exists(session, Meta, meta_id, label="Meta")
    meta = await services.update_meta(
        session,
        meta,
        app_version=data.app_version,
        extraction_timestamp=data.extraction_timestamp,
        parsing_timestamp=data.parsing_timestamp,
        source_url=data.source_url,
        custom_data=data.custom_data,
        vacancy_id=data.vacancy_id,
        company_id=data.company_id,
    )
    await session.refresh(meta)
    return dtos.MetaResponse.model_validate(meta)


async def delete_meta(
    session: AsyncSession, meta_id: int, hard_delete: bool = False
) -> dtos.MetaResponse:
    meta = await shared_services.ensure_exists(
        session, Meta, meta_id, include_deleted=True, label="Meta"
    )
    if hard_delete:
        response = dtos.MetaResponse.model_validate(meta)
        await services.delete_meta(session, meta, hard_delete=True)
        return response
    meta = await services.delete_meta(session, meta)
    await session.refresh(meta)
    return dtos.MetaResponse.model_validate(meta)
