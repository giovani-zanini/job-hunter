"""Link use cases.

This module contains all use case functions for managing user links.
Use cases orchestrate calls to service layer functions and handle
transaction management (commit/rollback).

The module organizes use cases into the following groups:
    - Core Link Operations: CRUD operations for links

Each use case function is responsible for:
    - Calling the appropriate service layer function(s)
    - Managing database transactions
    - Transforming models to response DTOs
    - Returning standardized responses
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.link import dtos
from src.modules.profile.features.link import services
from src.modules.profile.features.link.models import Link
from src.shared import services as shared_services


# --- Core Link Operations ---


async def create_link(
    session: AsyncSession, user_id: int, data: dtos.LinkCreateRequest
) -> dtos.LinkResponse:
    """Create a new user link.

    Args:
        session: The async database session for executing queries.
        data: The link creation request containing type, from_, and value.

    Returns:
        A LinkResponse containing the created link data.
    """
    # Create link
    link = await services.create_link(
        session=session,
        user_id=user_id,
        type=data.type.value,
        from_=data.from_,
        value=data.value,
    )

    await session.refresh(link)

    return dtos.LinkResponse.model_validate(link)


async def delete_link(
    session: AsyncSession, link_id: int, hard_delete: bool = False
) -> dtos.LinkResponse:
    """Delete a user link (soft or hard delete).

    Args:
        session: The async database session for executing queries.
        link_id: The unique identifier of the link to delete.
        hard_delete: If True, permanently removes the link from database.
            If False, performs a soft delete by setting deleted_at timestamp.
            Defaults to False.

    Returns:
        A LinkResponse containing the deleted link data.

    Raises:
        NotFoundException: If no link exists with the given link_id.
    """
    # Find link
    link = await shared_services.ensure_exists(
        session, Link, link_id, include_deleted=True, label="Link"
    )


    if hard_delete:
        response = dtos.LinkResponse.model_validate(link)
        await services.delete_link(session, link, hard_delete=True)

        return response

    link = await services.delete_link(session, link, hard_delete=False)

    await session.refresh(link)

    return dtos.LinkResponse.model_validate(link)


async def get_link(
    session: AsyncSession, link_id: int, include_deleted: bool = False
) -> dtos.LinkDetailResponse:
    """Retrieve a single link by its ID.

    Args:
        session: The async database session for executing queries.
        link_id: The unique identifier of the link to retrieve.
        include_deleted: Whether to include soft-deleted links. Defaults to False.

    Returns:
        A LinkDetailResponse containing the complete link data.

    Raises:
        NotFoundException: If no link exists with the given link_id.
    """
    # Find link
    link = await shared_services.ensure_exists(
        session, Link, link_id, include_deleted=include_deleted, label="Link"
    )

    return dtos.LinkDetailResponse.model_validate(link)


async def list_links(
    session: AsyncSession, filters: dtos.LinkFilterParams
) -> list[dtos.LinkResponse]:
    """List links with optional filtering and pagination.

    Args:
        session: The async database session for executing queries.
        filters: Filter parameters including skip, limit, user_id, type,
            from_, and include_deleted flags.

    Returns:
        A list of LinkResponse objects matching the filter criteria.
    """
    links = await services.get_all_links(
        session=session,
        skip=filters.skip,
        limit=filters.limit,
        user_id=filters.user_id,
        type_filter=filters.type.value if filters.type else None,
        from_filter=filters.from_,
        include_deleted=filters.include_deleted,
    )
    return [dtos.LinkResponse.model_validate(link) for link in links]


async def update_link(
    session: AsyncSession, link_id: int, data: dtos.LinkUpdateRequest,
) -> dtos.LinkResponse:
    """Update an existing user link.

    Args:
        session: The async database session for executing queries.
        link_id: The unique identifier of the link to update.
        data: The link update request containing optional type, from_, and value fields.

    Returns:
        A LinkResponse containing the updated link data.

    Raises:
        NotFoundException: If no link exists with the given link_id.
    """
    # Find link
    link = await shared_services.ensure_exists(session, Link, link_id, label="Link")


    # Update link
    link = await services.update_link(
        session=session,
        link=link,
        type=data.type.value if data.type else None,
        from_=data.from_,
        value=data.value,
    )

    await session.refresh(link)

    return dtos.LinkResponse.model_validate(link)
