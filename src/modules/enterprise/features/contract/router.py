"""Contract router — CRUD endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.shared.adapters import get_current_user, require_role
from src.modules.enterprise.shared.dtos import AuthenticatedUser
from src.modules.enterprise.features.contract import dtos, handlers
from src.shared.database import sql_client

_require_default_role = require_role(["default"])
router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("/", response_model=dtos.ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    data: dtos.ContractCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.ContractResponse:
    return await handlers.create_contract(session, data)


@router.get("/", response_model=List[dtos.ContractResponse])
async def list_contracts(
    type: Optional[str] = Query(None),
    regional_classification: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> List[dtos.ContractResponse]:
    filters = dtos.ContractFilterParams(
        type=type, regional_classification=regional_classification,
        include_deleted=include_deleted, skip=skip, limit=limit,
    )
    return await handlers.list_contracts(session, filters)


@router.get("/{contract_id}", response_model=dtos.ContractDetailResponse)
async def get_contract(
    contract_id: int,
    include_deleted: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.ContractDetailResponse:
    return await handlers.get_contract(session, contract_id, include_deleted)


@router.put("/{contract_id}", response_model=dtos.ContractResponse)
async def update_contract(
    contract_id: int,
    data: dtos.ContractUpdateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.ContractResponse:
    return await handlers.update_contract(session, contract_id, data)


@router.delete("/{contract_id}", response_model=dtos.ContractResponse)
async def delete_contract(
    contract_id: int,
    hard_delete: bool = Query(False),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    current_user: AuthenticatedUser = Depends(get_current_user),
    _: None = Depends(_require_default_role),
) -> dtos.ContractResponse:
    return await handlers.delete_contract(session, contract_id, hard_delete)
