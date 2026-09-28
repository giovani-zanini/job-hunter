"""Session service for database operations."""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared import exceptions
from src.modules.auth.features.session.models import Session
from src.modules.auth.shared.config import settings


# ---------------------------------------------------------------------------
# Security helpers
# ---------------------------------------------------------------------------


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token using SHA-256 for storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def create_session(
    db_session: AsyncSession,
    user_id: int,
    refresh_token: str,
    ip_address: str,
    user_agent: str,
) -> Session:
    """Create a new session record."""
    token_hash = hash_refresh_token(refresh_token)
    session_record = Session(
        user_id=user_id,
        refresh_token_hash=token_hash,
        refresh_token_expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db_session.add(session_record)
    await db_session.flush()
    return session_record


async def get_session_by_refresh_token(
    db_session: AsyncSession, refresh_token: str
) -> Session:
    """Find a session by its hashed refresh token."""
    token_hash = hash_refresh_token(refresh_token)
    stmt = select(Session).where(
        Session.refresh_token_hash == token_hash,
        Session.is_revoked.is_(False),
    )
    result = await db_session.execute(stmt)
    result = result.unique().scalar_one_or_none()
    if not result:
        raise exceptions.ForbiddenException(
            detail="Session not found or already revoked"
        )
    return result


async def revoke_session(
    db_session: AsyncSession,
    session_record: Session,
) -> None:
    """Revoke a single session."""
    if session_record.is_revoked:
        raise exceptions.ConflictException(detail="Session is already revoked")
    session_record.is_revoked = True
    await db_session.flush()


async def revoke_session_by_expiration_date(
    db_session: AsyncSession,
    session_record: Session,
) -> None:
    """Revoke a single session."""
    if session_record.is_revoked:
        raise exceptions.ConflictException(detail="Session is already revoked")
    if is_expired(session_record):
        session_record.is_revoked = True
        await db_session.flush()
        raise exceptions.UnauthorizedException(detail="Refresh token has expired")


async def revoke_all_user_sessions(db_session: AsyncSession, user_id: int) -> int:
    """Revoke all active sessions for a user. Returns count of revoked sessions."""
    stmt = (
        update(Session)
        .where(Session.user_id == user_id, Session.is_revoked.is_(False))
        .values(is_revoked=True)
    )
    result = await db_session.execute(stmt)
    await db_session.flush()
    return result.rowcount


async def update_last_used(
    db_session: AsyncSession, session_record: Session
) -> Session:
    """Update the last_used_at timestamp."""
    session_record.last_used_at = datetime.now(timezone.utc)
    await db_session.flush()
    return session_record


def is_expired(session_record: Session) -> bool:
    """Check if a session's refresh token has expired."""
    return datetime.now(timezone.utc) > session_record.refresh_token_expires_at


async def get_user_sessions(
    db_session: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    is_revoked: Optional[bool] = None,
) -> Sequence[Session]:
    """Get all sessions for a user."""
    stmt = select(Session).where(Session.user_id == user_id)

    if is_revoked is not None:
        stmt = stmt.where(Session.is_revoked == is_revoked)

    stmt = stmt.order_by(Session.created_at.desc()).offset(skip).limit(limit)
    result = await db_session.execute(stmt)
    return result.scalars().all()
