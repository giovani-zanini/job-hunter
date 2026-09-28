"""Contract service — database operations."""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.contract.models import Contract
from src.shared import services as shared_services


async def get_all_contracts(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    type_filter: Optional[str] = None,
    regional_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[Contract]:
    stmt = select(Contract)
    if not include_deleted:
        stmt = stmt.where(Contract.deleted_at.is_(None))
    if type_filter:
        stmt = stmt.where(Contract.type.ilike(f"%{type_filter}%"))
    if regional_filter:
        stmt = stmt.where(Contract.regional_classification.ilike(f"%{regional_filter}%"))
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_contract(session: AsyncSession, **fields) -> Contract:
    return await shared_services.create(session, Contract, **fields)


async def update_contract(session: AsyncSession, contract: Contract, **fields) -> Contract:
    for k, v in fields.items():
        if v is not None:
            setattr(contract, k, v)
    await session.flush()
    return contract


async def delete_contract(
    session: AsyncSession, contract: Contract, hard_delete: bool = False
) -> Contract:
    return await shared_services.delete(session, contract, hard_delete)
