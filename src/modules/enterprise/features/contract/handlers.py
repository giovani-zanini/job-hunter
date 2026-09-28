"""Contract use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.enterprise.features.contract import dtos, services
from src.modules.enterprise.features.contract.models import Contract
from src.shared import services as shared_services


async def create_contract(
    session: AsyncSession, data: dtos.ContractCreateRequest
) -> dtos.ContractResponse:
    contract = await services.create_contract(session, **data.model_dump())
    await session.refresh(contract)
    return dtos.ContractResponse.model_validate(contract)


async def get_contract(
    session: AsyncSession, contract_id: int, include_deleted: bool = False
) -> dtos.ContractDetailResponse:
    contract = await shared_services.ensure_exists(
        session, Contract, contract_id, include_deleted=include_deleted, label="Contract"
    )
    return dtos.ContractDetailResponse.model_validate(contract)


async def list_contracts(
    session: AsyncSession, filters: dtos.ContractFilterParams
) -> list[dtos.ContractResponse]:
    contracts = await services.get_all_contracts(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        type_filter=filters.type,
        regional_filter=filters.regional_classification,
        include_deleted=filters.include_deleted,
    )
    return [dtos.ContractResponse.model_validate(c) for c in contracts]


async def update_contract(
    session: AsyncSession, contract_id: int, data: dtos.ContractUpdateRequest
) -> dtos.ContractResponse:
    contract = await shared_services.ensure_exists(
        session, Contract, contract_id, label="Contract"
    )
    contract = await services.update_contract(
        session, contract, **data.model_dump(exclude_none=True)
    )
    await session.refresh(contract)
    return dtos.ContractResponse.model_validate(contract)


async def delete_contract(
    session: AsyncSession, contract_id: int, hard_delete: bool = False
) -> dtos.ContractResponse:
    contract = await shared_services.ensure_exists(
        session, Contract, contract_id, include_deleted=True, label="Contract"
    )
    if hard_delete:
        response = dtos.ContractResponse.model_validate(contract)
        await services.delete_contract(session, contract, hard_delete=True)
        return response
    contract = await services.delete_contract(session, contract)
    await session.refresh(contract)
    return dtos.ContractResponse.model_validate(contract)
