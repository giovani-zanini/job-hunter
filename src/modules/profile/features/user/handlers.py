"""Use cases for local profile owners."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.user import dtos, services
from src.modules.profile.features.user.models import User
from src.shared import services as shared_services


async def resolve_anonymous_user(session: AsyncSession) -> User:
    return await services.get_or_create_anonymous_user(session)


async def delete_user(
    session: AsyncSession, user_id: int, hard_delete: bool = False
) -> dtos.UserResponse:
    user = await shared_services.ensure_exists(
        session, User, user_id, include_deleted=True, label="User"
    )
    response = dtos.UserResponse.model_validate(user)
    user = await services.delete_user(session, user, hard_delete=hard_delete)
    if hard_delete:
        return response
    await session.refresh(user)
    return dtos.UserResponse.model_validate(user)


async def get_user(
    session: AsyncSession, user_id: int, include_deleted: bool = False
) -> dtos.UserDetailResponse:
    user = await shared_services.ensure_exists(
        session, User, user_id, include_deleted=include_deleted, label="User"
    )
    return dtos.UserDetailResponse.model_validate(user)


async def list_users(
    session: AsyncSession, filters: dtos.UserFilterParams
) -> list[dtos.UserResponse]:
    users = await services.get_all_users(
        session,
        skip=filters.skip,
        limit=filters.limit,
        is_anonymous_filter=filters.is_anonymous,
        include_deleted=filters.include_deleted,
    )
    return [dtos.UserResponse.model_validate(user) for user in users]
