"""Company use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.company import dtos, services
from src.modules.enterprise.features.company.models import EnterpriseCompany, CompanyUnit, CompanySegment
from src.modules.enterprise.features.location.models import Location
from src.modules.enterprise.features.segment.models import Segment
from src.shared import exceptions, services as shared_services
from src.shared import dtos as shared_dtos


async def create_company(
    session: AsyncSession, data: dtos.CompanyCreateRequest
) -> dtos.CompanyResponse:
    await shared_services.ensure_unique(session, EnterpriseCompany, "name", data.name, label="Company")
    company = await services.create_company(session, name=data.name)
    await session.refresh(company)
    return dtos.CompanyResponse.model_validate(company)


async def get_company(
    session: AsyncSession, company_id: int, include_deleted: bool = False
) -> dtos.CompanyDetailResponse:
    company = await shared_services.ensure_exists(
        session, EnterpriseCompany, company_id, include_deleted=include_deleted, label="Company"
    )
    return dtos.CompanyDetailResponse.model_validate(company)


async def list_companies(
    session: AsyncSession, filters: dtos.CompanyFilterParams
) -> list[dtos.CompanyResponse]:
    companies = await services.get_all_companies(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        name_filter=filters.name,
        include_deleted=filters.include_deleted,
    )
    return [dtos.CompanyResponse.model_validate(c) for c in companies]


async def update_company(
    session: AsyncSession, company_id: int, data: dtos.CompanyUpdateRequest
) -> dtos.CompanyResponse:
    company = await shared_services.ensure_exists(
        session, EnterpriseCompany, company_id, label="Company"
    )
    if data.name and data.name != company.name:
        await shared_services.ensure_unique(
            session, EnterpriseCompany, "name", data.name, exclude_id=company.id, label="Company"
        )
    company = await services.update_company(session, company, name=data.name)
    await session.refresh(company)
    return dtos.CompanyResponse.model_validate(company)


async def delete_company(
    session: AsyncSession, company_id: int, hard_delete: bool = False
) -> dtos.CompanyResponse:
    company = await shared_services.ensure_exists(
        session, EnterpriseCompany, company_id, include_deleted=True, label="Company"
    )
    if hard_delete:
        response = dtos.CompanyResponse.model_validate(company)
        await services.delete_company(session, company, hard_delete=True)
        return response
    company = await services.delete_company(session, company)
    await session.refresh(company)
    return dtos.CompanyResponse.model_validate(company)


# --- CompanyUnit use cases ---

async def add_unit(
    session: AsyncSession, company_id: int, data: dtos.CompanyUnitCreateRequest
) -> dtos.CompanyUnitResponse:
    await shared_services.ensure_exists(session, EnterpriseCompany, company_id, label="Company")
    await shared_services.ensure_exists(session, Location, data.location_id, label="Location")
    existing = await services.find_unit_by_company_location(session, company_id, data.location_id)
    if existing:
        raise exceptions.ConflictException(
            detail=f"CompanyUnit with company_id={company_id} and location_id={data.location_id} already exists"
        )
    unit = await services.create_unit(session, company_id=company_id, location_id=data.location_id)
    await session.refresh(unit)
    return dtos.CompanyUnitResponse.model_validate(unit)


async def list_units(
    session: AsyncSession, company_id: int
) -> list[dtos.CompanyUnitResponse]:
    await shared_services.ensure_exists(session, EnterpriseCompany, company_id, label="Company")
    units = await services.get_units_by_company(session, company_id)
    return [dtos.CompanyUnitResponse.model_validate(u) for u in units]


async def remove_unit(
    session: AsyncSession, company_id: int, unit_id: int
) -> None:
    await shared_services.ensure_exists(session, EnterpriseCompany, company_id, label="Company")
    unit = await shared_services.ensure_exists(session, CompanyUnit, unit_id, label="CompanyUnit")
    if unit.company_id != company_id:
        raise exceptions.NotFoundException(detail="CompanyUnit does not belong to this company.")
    await services.delete_unit(session, unit)


# --- CompanySegment use cases ---

async def add_segment(
    session: AsyncSession, company_id: int, segment_id: int
) -> dtos.CompanySegmentResponse:
    await shared_services.ensure_exists(session, EnterpriseCompany, company_id, label="Company")
    await shared_services.ensure_exists(session, Segment, segment_id, label="Segment")
    existing = await services.find_company_segment(session, company_id, segment_id)
    if existing:
        raise exceptions.ConflictException(
            detail=f"Segment {segment_id} already associated with company {company_id}"
        )
    cs = await services.create_company_segment(session, company_id=company_id, segment_id=segment_id)
    await session.refresh(cs)
    return dtos.CompanySegmentResponse.model_validate(cs)


async def list_segments(
    session: AsyncSession, company_id: int
) -> list[dtos.CompanySegmentResponse]:
    await shared_services.ensure_exists(session, EnterpriseCompany, company_id, label="Company")
    segments = await services.get_segments_by_company(session, company_id)
    return [dtos.CompanySegmentResponse.model_validate(s) for s in segments]


async def remove_segment(
    session: AsyncSession, company_id: int, segment_id: int
) -> None:
    await shared_services.ensure_exists(session, EnterpriseCompany, company_id, label="Company")
    cs = await services.find_company_segment(session, company_id, segment_id)
    if not cs:
        raise exceptions.NotFoundException(
            detail=f"Segment {segment_id} not associated with company {company_id}"
        )
    await services.delete_company_segment(session, cs)
