"""Meta service — database operations."""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.meta.models import Meta
from src.shared import services as shared_services


async def get_all_metas(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    vacancy_id_filter: Optional[int] = None,
    company_id_filter: Optional[int] = None,
    include_deleted: bool = False,
) -> Sequence[Meta]:
    stmt = select(Meta)
    if not include_deleted:
        stmt = stmt.where(Meta.deleted_at.is_(None))
    if vacancy_id_filter is not None:
        stmt = stmt.where(Meta.vacancy_id == vacancy_id_filter)
    if company_id_filter is not None:
        stmt = stmt.where(Meta.company_id == company_id_filter)
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_meta(session: AsyncSession, **fields) -> Meta:
    return await shared_services.create(session, Meta, **fields)


async def update_meta(session: AsyncSession, meta: Meta, **kwargs) -> Meta:
    for key, value in kwargs.items():
        if value is not None:
            setattr(meta, key, value)
    await session.flush()
    return meta


async def delete_meta(
    session: AsyncSession, meta: Meta, hard_delete: bool = False
) -> Meta:
    return await shared_services.delete(session, meta, hard_delete)
