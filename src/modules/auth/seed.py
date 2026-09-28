"""Seed utilities for auth module."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.modules.auth.features.role.dtos import CreateRoleRequest
from src.modules.auth.features.role import handlers as role_handlers


async def seed_roles(
    session: AsyncSession,
    roles: List[CreateRoleRequest],
) -> None:
    """Seed roles into the database using insert-if-not-exists logic.

    Delegates to the auth module's role handler so all role creation
    rules (unique-name check, commit) are applied consistently.

    Args:
        session: Async database session (write).
        roles: List of role definitions to seed.
    """
    await role_handlers.create_roles(session, roles)