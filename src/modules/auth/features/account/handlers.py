"""User use cases (auth module).

User creation is atomic: creates User + Auth in a single transaction.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared import exceptions
from src.modules.auth.features.identity.models import Auth
from src.modules.auth.features.role.models import Role
from src.modules.auth.features.account import dtos
from src.modules.auth.features.account import services
from src.modules.auth.features.account.models import UserAccount
from src.modules.auth.shared.utils import hash_password
from src.shared import services as shared_services


async def create_user(
    session: AsyncSession, data: dtos.UserCreateRequest
) -> dtos.UserResponse:
    """Create a new user with auth credentials (atomic)."""
    await shared_services.ensure_unique(
        session, UserAccount, "email", data.email, include_deleted=True, label="User"
    )
    role = await shared_services.get_one_by_field(
        session=session,
        model=Role,
        field_name="name",
        field_value="default",
        raise_not_found_exception=True,
    )

    # Create user
    user = await services.create_user(session, email=data.email, role_id=role.id)

    # Create associated auth record (atomic)
    password_hash = hash_password(data.password)
    auth = Auth(user_id=user.id, password_hash=password_hash)
    session.add(auth)

    await session.refresh(user, attribute_names=["role", "auth"])

    return dtos.UserResponse.model_validate(user)


async def get_user(session: AsyncSession, user_id: int) -> dtos.UserResponse:
    """Get a user by ID."""
    user = await shared_services.get_one_by_field(
        session=session,
        model=UserAccount,
        field_name="id",
        field_value=user_id,
        raise_not_found_exception=True,
    )
    return dtos.UserResponse.model_validate(user)


async def list_users(
    session: AsyncSession, filters: dtos.UserFilterParams
) -> list[dtos.UserResponse]:
    """List users with optional filters."""
    users = await services.get_all_users(
        session,
        skip=filters.skip,
        limit=filters.limit,
        email_filter=filters.email,
        role_id_filter=filters.role_id,
        is_active_filter=filters.is_active,
    )
    return [dtos.UserResponse.model_validate(u) for u in users]


async def delete_user(session: AsyncSession, user_id: int) -> None:
    """Hard delete a user (cascades to auth + sessions)."""
    user = await shared_services.get_one_by_field(
        session=session,
        model=UserAccount,
        field_name="id",
        field_value=user_id,
        raise_not_found_exception=True,
    )
    await session.delete(user)
