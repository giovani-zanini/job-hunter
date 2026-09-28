"""Company use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.company import dtos
from src.modules.profile.features.company import services
from src.modules.profile.features.company.models import Company
from src.shared import services as shared_services


async def create_company(
    session: AsyncSession, data: dtos.CompanyCreateRequest
) -> dtos.CompanyResponse:
    """Execute the create company use case."""

    # Check if company name already exists
    await shared_services.ensure_unique(
        session,
        Company,
        "name",
        data.name,
        include_deleted=True,
        label="Company",
    )

    # Create company
    company = await services.create_company(
        session=session,
        name=data.name,
        website=data.website,
    )

    await session.refresh(company)

    return dtos.CompanyResponse.model_validate(company)


async def delete_company(
    session: AsyncSession, company_id: int, hard_delete: bool = False
) -> dtos.CompanyResponse:
    """Execute the delete company use case."""

    # Find company
    company = await shared_services.ensure_exists(
        session, Company, company_id, include_deleted=True, label="Company"
    )

    if hard_delete:
        response = dtos.CompanyResponse.model_validate(company)
        await services.delete_company(session, company, hard_delete=True)

        return response

    company = await services.delete_company(session, company, hard_delete=False)

    await session.refresh(company)

    return dtos.CompanyResponse.model_validate(company)


async def get_company(
    session: AsyncSession, company_id: int, include_deleted: bool = False
) -> dtos.CompanyDetailResponse:
    """Execute the get company use case."""

    # Find company
    company = await shared_services.ensure_exists(
        session, Company, company_id, include_deleted=include_deleted, label="Company"
    )

    return dtos.CompanyDetailResponse.model_validate(company)


async def list_companies(
    session: AsyncSession, filters: dtos.CompanyFilterParams
) -> list[dtos.CompanyResponse]:
    """Execute the list companies use case."""

    companies = await services.get_all_companies(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        name_filter=filters.name,
        include_deleted=filters.include_deleted,
    )
    return [dtos.CompanyResponse.model_validate(company) for company in companies]


async def update_company(
    session: AsyncSession, company_id: int, data: dtos.CompanyUpdateRequest
) -> dtos.CompanyResponse:
    """Execute the update company use case."""

    # Find company
    company = await shared_services.ensure_exists(
        session, Company, company_id, label="Company"
    )

    # Check name uniqueness if changing
    if data.name and data.name != company.name:
        await shared_services.ensure_unique(
            session,
            Company,
            "name",
            data.name,
            include_deleted=True,
            label="Company",
            exclude_id=company.id,
        )

    # Update company
    company = await services.update_company(
        session=session,
        company=company,
        name=data.name,
        website=data.website,
    )

    await session.refresh(company)

    return dtos.CompanyResponse.model_validate(company)
