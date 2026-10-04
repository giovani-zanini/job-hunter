"""Company feature router with CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.company import dtos
from src.modules.profile.features.company import handlers
from src.shared.database import sql_client


router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post(
    "/",
    response_model=dtos.CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new company",
)
async def create_company(
    data: dtos.CompanyCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.CompanyResponse:
    """Create a new company with the provided name and website."""
    return await handlers.create_company(session, data)


@router.get(
    "/",
    response_model=List[dtos.CompanyResponse],
    summary="List all companies",
)
async def list_companies(
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    include_deleted: bool = Query(False, description="Include soft deleted companies"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
) -> List[dtos.CompanyResponse]:
    """List all companies with optional filters and pagination."""
    filters = dtos.CompanyFilterParams(
        name=name,
        include_deleted=include_deleted,
        skip=skip,
        limit=limit,
    )
    return await handlers.list_companies(session, filters)


@router.get(
    "/{company_id}",
    response_model=dtos.CompanyDetailResponse,
    summary="Get a company by ID",
)
async def get_company(
    company_id: int,
    include_deleted: bool = Query(False, description="Include if soft deleted"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
) -> dtos.CompanyDetailResponse:
    """Get a specific company by its ID."""
    return await handlers.get_company(session, company_id, include_deleted)


@router.put(
    "/{company_id}",
    response_model=dtos.CompanyResponse,
    summary="Update a company",
)
async def update_company(
    company_id: int,
    data: dtos.CompanyUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.CompanyResponse:
    """Update a company's information."""
    return await handlers.update_company(session, company_id, data)


@router.delete(
    "/{company_id}",
    response_model=dtos.CompanyResponse,
    summary="Delete a company",
)
async def delete_company(
    company_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the company"),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.CompanyResponse:
    """Soft delete a company (or hard delete if specified)."""
    return await handlers.delete_company(session, company_id, hard_delete)
