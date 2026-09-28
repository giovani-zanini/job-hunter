"""Role handlers (use cases) for the auth module."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared import services as shared_services
from src.modules.auth.features.role import dtos, services
from src.modules.auth.features.role.models import Role


async def create_roles(
    session: AsyncSession,
    roles: list[dtos.CreateRoleRequest],
) -> None:
    """Create roles that do not yet exist (insert-if-not-exists).

    Args:
        session: Database session
        roles: List of role create requests
    """
    for role_data in roles:
        existing = await shared_services.get_one_by_field(
            session, Role, "name", role_data.name, include_deleted=False
        )
        if existing:
            continue

        await services.create_role(
            session,
            name=role_data.name,
            description=role_data.description,
        )
