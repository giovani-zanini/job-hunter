"""Company service — database operations."""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.company.models import EnterpriseCompany, CompanyUnit, CompanySegment
from src.shared import services as shared_services


async def get_all_companies(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    name_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[EnterpriseCompany]:
    stmt = select(EnterpriseCompany)
    if not include_deleted:
        stmt = stmt.where(EnterpriseCompany.deleted_at.is_(None))
    if name_filter:
        stmt = stmt.where(EnterpriseCompany.name.ilike(f"%{name_filter}%"))
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_company(session: AsyncSession, name: str) -> EnterpriseCompany:
    return await shared_services.create(session, EnterpriseCompany, name=name)


async def update_company(
    session: AsyncSession, company: EnterpriseCompany, name: Optional[str] = None
) -> EnterpriseCompany:
    if name is not None:
        company.name = name
    await session.flush()
    return company


async def delete_company(
    session: AsyncSession, company: EnterpriseCompany, hard_delete: bool = False
) -> EnterpriseCompany:
    return await shared_services.delete(session, company, hard_delete)


# --- CompanyUnit ---

async def get_units_by_company(
    session: AsyncSession, company_id: int
) -> Sequence[CompanyUnit]:
    stmt = select(CompanyUnit).where(CompanyUnit.company_id == company_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_unit(
    session: AsyncSession, unit_id: int
) -> Optional[CompanyUnit]:
    return await shared_services.get_one_by_field(session, CompanyUnit, "id", unit_id)


async def find_unit_by_company_location(
    session: AsyncSession, company_id: int, location_id: int
) -> Optional[CompanyUnit]:
    stmt = select(CompanyUnit).where(
        CompanyUnit.company_id == company_id,
        CompanyUnit.location_id == location_id,
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def create_unit(
    session: AsyncSession, company_id: int, location_id: int
) -> CompanyUnit:
    return await shared_services.create(
        session, CompanyUnit, company_id=company_id, location_id=location_id
    )


async def delete_unit(session: AsyncSession, unit: CompanyUnit) -> None:
    await session.delete(unit)
    await session.flush()


# --- CompanySegment ---

async def get_segments_by_company(
    session: AsyncSession, company_id: int
) -> Sequence[CompanySegment]:
    stmt = select(CompanySegment).where(CompanySegment.company_id == company_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def find_company_segment(
    session: AsyncSession, company_id: int, segment_id: int
) -> Optional[CompanySegment]:
    stmt = select(CompanySegment).where(
        CompanySegment.company_id == company_id,
        CompanySegment.segment_id == segment_id,
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def create_company_segment(
    session: AsyncSession, company_id: int, segment_id: int
) -> CompanySegment:
    return await shared_services.create(
        session, CompanySegment, company_id=company_id, segment_id=segment_id
    )


async def delete_company_segment(
    session: AsyncSession, company_segment: CompanySegment
) -> None:
    await session.delete(company_segment)
    await session.flush()
