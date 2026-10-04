"""Education feature router with CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.education import dtos
from src.modules.profile.features.education import handlers
from src.modules.profile.shared.adapters import get_anonymous_user_id
from src.shared.database import sql_client
from src.shared import dtos as shared_dtos


router = APIRouter(prefix="/education", tags=["Education"])


# --- Education CRUD ---


@router.post(
    "/",
    response_model=dtos.EducationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new education record",
)
async def create_education(
    data: dtos.EducationCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    anonymous_user_id: int = Depends(get_anonymous_user_id),
) -> dtos.EducationDetailResponse:
    """Create a new education record with optional skills."""
    return await handlers.create_education(session, anonymous_user_id, data)


@router.get(
    "/",
    response_model=List[dtos.EducationResponse],
    summary="List all education records",
)
async def list_education(
    institution_name: Optional[str] = Query(
        None, description="Filter by institution (partial)"
    ),
    degree: Optional[str] = Query(None, description="Filter by degree (partial match)"),
    field_of_study: Optional[str] = Query(
        None, description="Filter by field (partial match)"
    ),
    include_deleted: bool = Query(False, description="Include soft deleted records"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
) -> List[dtos.EducationResponse]:
    """List education records."""
    filters = dtos.EducationFilterParams(
        institution_name=institution_name,
        degree=degree,
        field_of_study=field_of_study,
        include_deleted=include_deleted,
        skip=skip,
        limit=limit,
    )
    return await handlers.list_education(session, filters)


@router.get(
    "/{education_id}",
    response_model=dtos.EducationDetailResponse,
    summary="Get an education record by ID",
)
async def get_education(
    education_id: int,
    include_deleted: bool = Query(False, description="Include if soft deleted"),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
) -> dtos.EducationDetailResponse:
    """Get a specific education record by its ID."""
    return await handlers.get_education(session, education_id, include_deleted)


@router.put(
    "/{education_id}",
    response_model=dtos.EducationResponse,
    summary="Update an education record",
)
async def update_education(
    education_id: int,
    data: dtos.EducationUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.EducationResponse:
    """Update an education record's information."""
    return await handlers.update_education(session, education_id, data)


@router.delete(
    "/{education_id}",
    response_model=dtos.EducationResponse,
    summary="Delete an education record",
)
async def delete_education(
    education_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the record"),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.EducationResponse:
    """Soft delete an education record (or hard delete if specified)."""
    return await handlers.delete_education(
        session, education_id, hard_delete
    )


# --- Education Skills ---


@router.post(
    "/{education_id}/skills/{skill_id}",
    response_model=shared_dtos.Message,
    status_code=status.HTTP_201_CREATED,
    summary="Add a skill to an education",
)
async def add_education_skill(
    education_id: int,
    skill_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> shared_dtos.Message:
    """Associate a skill with an education record."""
    return await handlers.add_education_skill(session, education_id, skill_id)


@router.delete(
    "/{education_id}/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a skill from an education",
)
async def remove_education_skill(
    education_id: int,
    skill_id: int,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> None:
    """Remove a skill from an education record."""
    await handlers.remove_education_skill(session, education_id, skill_id)
