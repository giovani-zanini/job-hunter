"""Company service for database operations."""

from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.company.models import Company
from src.shared import services as shared_services


async def get_company_by_id(
    session: AsyncSession, company_id: int, include_deleted: bool = False
) -> Optional[Company]:
    """Get a company by ID."""
    return await shared_services.get_one_by_field(
        session, Company, "id", company_id, include_deleted
    )


async def get_company_by_name(
    session: AsyncSession, name: str, include_deleted: bool = False
) -> Optional[Company]:
    """Get a company by exact name."""
    return await shared_services.get_one_by_field(
        session, Company, "name", name, include_deleted
    )


async def get_all_companies(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    name_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[Company]:
    """Get all companies with optional filters."""
    stmt = select(Company)

    if not include_deleted:
        stmt = stmt.where(Company.deleted_at.is_(None))

    if name_filter:
        stmt = stmt.where(Company.name.ilike(f"%{name_filter}%"))

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_companies(
    session: AsyncSession,
    name_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> int:
    """Count companies with optional filters."""
    stmt = select(func.count(Company.id))

    if not include_deleted:
        stmt = stmt.where(Company.deleted_at.is_(None))

    if name_filter:
        stmt = stmt.where(Company.name.ilike(f"%{name_filter}%"))

    result = await session.execute(stmt)
    return result.unique().scalar_one()


async def create_company(session: AsyncSession, name: str, website: str) -> Company:
    """Create a new company."""
    return await shared_services.create(session, Company, name=name, website=website)


async def update_company(
    session: AsyncSession,
    company: Company,
    name: Optional[str] = None,
    website: Optional[str] = None,
) -> Company:
    """Update company fields."""
    if name is not None:
        company.name = name
    if website is not None:
        company.website = website
    await session.flush()
    return company


async def delete_company(
    session: AsyncSession, company: Company, hard_delete: bool = False
) -> Company:
    """Delete a company (soft or hard delete)."""
    return await shared_services.delete(session, company, hard_delete)
