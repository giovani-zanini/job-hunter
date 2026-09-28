"""FastAPI dependencies for the profile module.

``get_current_profile_user`` is the primary dependency used by all profile
feature routers. It composes over the auth module's ``get_current_user`` to:

1. Validate the Bearer JWT (delegated to the auth module – treated as a black box).
2. Look up the corresponding row in ``profile.User`` by ``external_id``.
3. If the row does not exist yet, auto-create it and commit within its own
   short-lived session so the write is independent of the caller's session.
4. Return a ``ProfileUser`` DTO that routers can use for scoping and ownership.

``require_role`` is re-exported from the auth module because role validation is
purely JWT-based and does not involve the profile database.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.shared.adapters import get_current_user
from src.modules.auth.shared.adapters import require_role  # re-export
from src.modules.auth.shared.dtos import AuthenticatedUser
from src.modules.profile.features.user import handlers as user_handlers
from src.modules.profile.shared.dtos import ProfileUser
from src.shared.database import sql_client


async def get_current_profile_user(
    auth_user: AuthenticatedUser = Depends(get_current_user),
    db_session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> ProfileUser:
    """Resolve (or auto-create) the profile.User row for the current request.

    Args:
        auth_user: The authenticated user DTO returned by the auth dependency.
        db_session: A writable async session used to look up / create the row.

    Returns:
        A ``ProfileUser`` containing the profile PK, the auth external ID, the
        JWT role name, and the active status.
    """
    # delegate lookup/creation logic to the user feature's handler
    # the handler returns a fully constructed ``User`` model instance,
    # creating it only when missing. this keeps business logic inside the
    # feature layer instead of the adapter.
    
    user = await user_handlers.resolve_or_create_user(db_session, auth_user.id)

    return ProfileUser(
        id=user.id,
        external_id=user.external_id,
        role_name=auth_user.role_name,
        is_active=auth_user.is_active,
    )


__all__ = ["get_current_profile_user", "require_role"]
