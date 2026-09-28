"""Use cases for the profile User feature."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.user import dtos
from src.modules.profile.features.user import services
from src.modules.profile.features.user.models import User
from src.modules.profile.shared.dtos import ProfileUser
from src.shared import services as shared_services


async def get_me(
    session: AsyncSession, current_user: ProfileUser
) -> dtos.UserDetailResponse:
    """Return the profile User record for the currently authenticated user."""
    user = await shared_services.ensure_exists(
        session, User, current_user.id, include_deleted=False, label="User"
    )
    return dtos.UserDetailResponse.model_validate(user)


async def delete_user(
    session: AsyncSession, user_id: int, hard_delete: bool = False
) -> dtos.UserResponse:
    """Execute the use case for deleting a user."""

    user = await shared_services.ensure_exists(
        session, User, user_id, include_deleted=True, label="User"
    )

    user = await services.delete_user(session, user, hard_delete=hard_delete)

    await session.refresh(user)

    return dtos.UserResponse.model_validate(user)


async def get_user(
    session: AsyncSession, user_id: int, include_deleted: bool = False
) -> dtos.UserDetailResponse:
    """Execute the use case for getting a user by ID."""

    user = await shared_services.ensure_exists(
        session, User, user_id, include_deleted=include_deleted, label="User"
    )

    return dtos.UserDetailResponse.model_validate(user)


async def list_users(
    session: AsyncSession, filters: dtos.UserFilterParams
) -> list[dtos.UserResponse]:
    """Execute the use case for listing users with optional filters and pagination."""

    users = await services.get_all_users(
        session,
        skip=filters.skip,
        limit=filters.limit,
        external_id_filter=filters.external_id,
        include_deleted=filters.include_deleted,
    )

    return [dtos.UserResponse.model_validate(user) for user in users]


async def resolve_or_create_user(session: AsyncSession, external_id: int) -> User:

    user = await services.get_user_by_external_id(
        session, external_id, include_deleted=False
    )
    user = await services.create_user_if_not_exists(session, external_id, user)
    return user
