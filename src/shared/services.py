from typing import List, Literal, Optional, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared import dtos
from src.shared import exceptions
from src.shared.database.sql_client import Base


T = TypeVar("T", bound=Base)


async def get_one_by_field[T](
    session: AsyncSession,
    model: T,
    field_name: str,
    field_value,
    include_deleted: bool = False,
    raise_not_found_exception: bool = False,
) -> Optional[T]:
    """Get a model by a specific field."""
    field = getattr(model, field_name)
    stmt = select(model).where(field == field_value)
    if not include_deleted and hasattr(model, "deleted_at"):
        stmt = stmt.where(model.deleted_at.is_(None))
    result = await session.execute(stmt)
    result = result.unique().scalar_one_or_none()
    if result is None and raise_not_found_exception:
        resolved_label = _resolve_label(model)
        raise exceptions.NotFoundException(
            detail=f"{resolved_label} with {field_name.upper()} {field_value} not found"
        )
    return result


async def get_many_by_field[T](
    session: AsyncSession,
    model: T,
    field_name: str,
    field_value,
    include_deleted: bool = False,
) -> Sequence[T]:
    """Get multiple models by a specific field."""
    field = getattr(model, field_name)
    stmt = select(model).where(field == field_value)
    if not include_deleted and hasattr(model, "deleted_at"):
        stmt = stmt.where(model.deleted_at.is_(None))
    result = await session.execute(stmt)
    return result.scalars().all()


def _resolve_label(model: T, label: str | None = None) -> str:
    return label or getattr(model, "__name__", "Resource")


async def ensure_exists[T](
    session: AsyncSession,
    model: T,
    entity_id,
    include_deleted: bool = False,
    label: Optional[str] = None,
    field_name: str = "id",
) -> T:
    """Ensure an entity exists or raise a standardized NotFoundException."""

    entity = await get_one_by_field(
        session, model, field_name, entity_id, include_deleted
    )
    if not entity:
        resolved_label = _resolve_label(model, label)
        raise exceptions.NotFoundException(
            detail=f"{resolved_label} with {field_name.upper()} {entity_id} not found"
        )
    return entity


async def ensure_batch_exists[T](
    session: AsyncSession,
    model: T,
    ids: List[int],
    *,
    include_deleted: bool = False,
    label: Optional[str] = None,
) -> Sequence[T]:
    """Ensure all IDs exist, raising NotFoundException with missing IDs when absent."""

    if not ids:
        return []

    items = await get_many_by_field(session, model, "id", ids, include_deleted)
    found_ids = {item.id for item in items}
    missing_ids = set(ids) - found_ids

    if missing_ids:
        resolved_label = _resolve_label(model, label)
        missing_sorted = sorted(missing_ids)
        raise exceptions.NotFoundException(
            detail=f"{resolved_label} not found: {missing_sorted}"
        )

    return items


async def ensure_unique[T](
    session: AsyncSession,
    model: T,
    field_name: str,
    value,
    *,
    include_deleted: bool = True,
    label: Optional[str] = None,
    exclude_id: Optional[int] = None,
) -> None:
    """Ensure a unique field value, optionally excluding a current entity ID."""

    existing = await get_one_by_field(
        session, model, field_name, value, include_deleted
    )
    if existing and (exclude_id is None or getattr(existing, "id", None) != exclude_id):
        resolved_label = _resolve_label(model, label)
        raise exceptions.ConflictException(
            detail=f"{resolved_label} with {field_name.upper()} '{value}' already exists"
        )


async def ensure_association[T](
    session: AsyncSession,
    model: T,
    config: dtos.Association,
    type: Literal["absent", "present"],
) -> None:
    """Ensure an association is either present or absent, raising appropriate exceptions."""

    stmt = select(model).where(
        getattr(model, config.left_field_name) == config.left_field_value,
        getattr(model, config.right_field_name) == config.right_field_value,
    )
    result = await session.execute(stmt)
    existing = result.unique().scalar_one_or_none()
    if type == "absent" and existing:
        raise exceptions.ConflictException(
            detail=f"{config.right_label} {config.right_field_value} already associated with {config.left_label} {config.left_field_value}"
        )
    if type == "present" and not existing:
        raise exceptions.NotFoundException(
            detail=f"{config.right_label} {config.right_field_value} not associated with {config.left_label} {config.left_field_value}"
        )
    return existing


async def delete[T](session: AsyncSession, model: T, hard_delete: bool = False) -> T:
    """Delete a model, either soft or hard delete.

    Returns the model instance. For soft deletes the model retains its updated
    ``deleted_at`` timestamp. For hard deletes the model is expired from the
    session but the Python object is still returned (do not refresh it).
    """

    if hard_delete:
        await session.delete(model)
    else:
        model.soft_delete()

    await session.flush()
    return model


async def create[T](session: AsyncSession, model: T, **fields) -> T:
    """Create a new model instance."""
    model = model(**fields)
    session.add(model)
    await session.flush()
    return model
