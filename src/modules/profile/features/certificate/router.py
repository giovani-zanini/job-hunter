"""Certificate feature router with CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.certificate import dtos
from src.modules.profile.features.certificate import handlers
from src.modules.profile.shared.adapters import get_anonymous_user_id
from src.shared.database import sql_client
from src.shared import dtos as shared_dtos


router = APIRouter(prefix="/certificates", tags=["Certificates"])


# --- Certificate CRUD ---


@router.post(
    "/",
    response_model=dtos.CertificateDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new certificate",
)
async def create_certificate(
    data: dtos.CertificateCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    anonymous_user_id: int = Depends(get_anonymous_user_id),
) -> dtos.CertificateDetailResponse:
    """Create a new certificate with optional skills."""
    return await handlers.create_certificate(session, anonymous_user_id, data)


@router.get(
    "/",
    response_model=List[dtos.CertificateResponse],
    summary="List all certificates",
)
async def list_certificates(
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    issuer: Optional[str] = Query(None, description="Filter by issuer (partial match)"),
    include_deleted: bool = Query(
        False, description="Include soft deleted certificates"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
) -> List[dtos.CertificateResponse]:
    """List certificates."""
    filters = dtos.CertificateFilterParams(
        name=name,
        issuer=issuer,
        include_deleted=include_deleted,
        skip=skip,
        limit=limit,
    )
    return await handlers.list_certificates(session, filters)


@router.get(
    "/{certificate_id}",
    response_model=dtos.CertificateDetailResponse,
    summary="Get a certificate by ID",
)
async def get_certificate(
    certificate_id: int,
    include_deleted: bool = Query(False, description="Include if soft deleted"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
) -> dtos.CertificateDetailResponse:
    """Get a specific certificate by its ID."""
    return await handlers.get_certificate(session, certificate_id, include_deleted)


@router.put(
    "/{certificate_id}",
    response_model=dtos.CertificateResponse,
    summary="Update a certificate",
)
async def update_certificate(
    certificate_id: int,
    data: dtos.CertificateUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.CertificateResponse:
    """Update a certificate's information."""
    return await handlers.update_certificate(
        session, certificate_id, data
    )


@router.delete(
    "/{certificate_id}",
    response_model=dtos.CertificateResponse,
    summary="Delete a certificate",
)
async def delete_certificate(
    certificate_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the record"),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.CertificateResponse:
    """Soft delete a certificate (or hard delete if specified)."""
    return await handlers.delete_certificate(
        session, certificate_id, hard_delete
    )


# --- Certificate Skills ---


@router.post(
    "/{certificate_id}/skills/{skill_id}",
    response_model=shared_dtos.Message,
    status_code=status.HTTP_201_CREATED,
    summary="Add a skill to a certificate",
)
async def add_certificate_skill(
    certificate_id: int,
    skill_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> shared_dtos.Message:
    """Associate a skill with a certificate."""
    return await handlers.add_certificate_skill(session, certificate_id, skill_id)


@router.delete(
    "/{certificate_id}/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a skill from a certificate",
)
async def remove_certificate_skill(
    certificate_id: int,
    skill_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> None:
    """Remove a skill from a certificate."""
    await handlers.remove_certificate_skill(session, certificate_id, skill_id)
