"""Link service for database operations.

This module provides service layer functions for managing user links and their
operations. All operations are performed asynchronously using SQLAlchemy AsyncSession.

The service handles:
    - CRUD operations for links (create, read, update, delete)
    - Link filtering and pagination
    - Link counting for statistics
    - Soft and hard deletion support
"""

from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.link.models import Link
from src.shared import services as shared_services


# --- Query Functions ---


async def get_link_by_id(
    session: AsyncSession, link_id: int, include_deleted: bool = False
) -> Optional[Link]:
    """Get a link by its unique identifier.

    Args:
        session: The async database session for executing queries.
        link_id: The unique identifier of the link to retrieve.
        include_deleted: Whether to include soft-deleted links in the search.
            Defaults to False.

    Returns:
        The link instance if found, None otherwise.
    """
    return await shared_services.get_one_by_field(
        session, Link, "id", link_id, include_deleted
    )


async def get_all_links(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[int] = None,
    type_filter: Optional[str] = None,
    from_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> Sequence[Link]:
    """Get all links with optional filters and pagination.

    Args:
        session: The async database session for executing queries.
        skip: Number of records to skip for pagination. Defaults to 0.
        limit: Maximum number of records to return. Defaults to 20.
        user_id: Filter links by user ID if provided.
        type_filter: Filter links by type classification if provided.
        from_filter: Case-insensitive partial match filter for link origin.
        include_deleted: Whether to include soft-deleted links. Defaults to False.

    Returns:
        A sequence of link instances matching the filters.
    """
    stmt = select(Link)

    if not include_deleted:
        stmt = stmt.where(Link.deleted_at.is_(None))

    if user_id:
        stmt = stmt.where(Link.user_id == user_id)

    if type_filter:
        stmt = stmt.where(Link.type == type_filter)

    if from_filter:
        stmt = stmt.where(Link.from_.ilike(f"%{from_filter}%"))

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_links(
    session: AsyncSession,
    user_id: Optional[int] = None,
    type_filter: Optional[str] = None,
    from_filter: Optional[str] = None,
    include_deleted: bool = False,
) -> int:
    """Count links with optional filters.

    Args:
        session: The async database session for executing queries.
        user_id: Filter count by user ID if provided.
        type_filter: Filter count by type classification if provided.
        from_filter: Case-insensitive partial match filter for link origin.
        include_deleted: Whether to include soft-deleted links. Defaults to False.

    Returns:
        The total count of links matching the filters.
    """
    stmt = select(func.count(Link.id))

    if not include_deleted:
        stmt = stmt.where(Link.deleted_at.is_(None))

    if user_id:
        stmt = stmt.where(Link.user_id == user_id)

    if type_filter:
        stmt = stmt.where(Link.type == type_filter)

    if from_filter:
        stmt = stmt.where(Link.from_.ilike(f"%{from_filter}%"))

    result = await session.execute(stmt)
    return result.unique().scalar_one()


# --- CRUD Functions ---


async def create_link(
    session: AsyncSession,
    user_id: int,
    type: str,
    from_: str,
    value: str,
) -> Link:
    """Create a new link.

    Args:
        session: The async database session for executing queries.
        user_id: The ID of the user who owns this link.
        type: Type classification of the link (SOCIAL_MEDIA, EMAIL, CELLPHONE).
        from_: Origin platform or service (gmail, linkedin, etc.).
        value: The actual link value (URL, email address, phone number).

    Returns:
        The newly created link instance.
    """
    return await shared_services.create(
        session, Link, user_id=user_id, type=type, from_=from_, value=value
    )


async def update_link(
    session: AsyncSession,
    link: Link,
    type: Optional[str] = None,
    from_: Optional[str] = None,
    value: Optional[str] = None,
) -> Link:
    """Update link fields.

    Only provided fields will be updated. Fields set to None are ignored.

    Args:
        session: The async database session for executing queries.
        link: The link instance to update.
        type: New type classification value.
        from_: New origin platform or service value.
        value: New link value (URL, email, phone number).

    Returns:
        The updated link instance.
    """
    if type is not None:
        link.type = type
    if from_ is not None:
        link.from_ = from_
    if value is not None:
        link.value = value
    await session.flush()
    return link


async def delete_link(
    session: AsyncSession, link: Link, hard_delete: bool = False
) -> Link:
    """Delete a link (soft or hard delete).

    Args:
        session: The async database session for executing queries.
        link: The link instance to delete.
        hard_delete: If True, permanently removes the record from database.
            If False, performs a soft delete by setting deleted_at timestamp.
            Defaults to False.

    Returns:
        The deleted link instance (for soft delete, contains updated deleted_at).
    """
    return await shared_services.delete(session, link, hard_delete)
