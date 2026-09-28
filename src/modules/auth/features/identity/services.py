"""Auth service for credential operations."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared import exceptions
from src.modules.auth.features.account.models import UserAccount
from src.modules.auth.features.identity.models import Auth
from src.modules.auth.shared.config import settings
from src.modules.auth.shared.utils import hash_password, verify_password
from src.shared import services as shared_services
from src.modules.auth.features.identity import dtos


# ---------------------------------------------------------------------------
# Security functions
# ---------------------------------------------------------------------------


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token. Raises JWTError on failure."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def decode_refresh_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT refresh token. Raises JWTError on failure."""
    return jwt.decode(
        token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM]
    )


def generate_recovery_token() -> str:
    """Generate a cryptographically secure 256-bit recovery token."""
    return secrets.token_urlsafe(32)


async def get_auth_by_user_id(session: AsyncSession, user_id: int) -> Optional[Auth]:
    """Get auth record by user ID."""
    stmt = select(Auth).where(Auth.user_id == user_id)
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_credentials_by_user_email(session: AsyncSession, email: str) -> Auth:
    stmt = (
        select(Auth)
        .join(UserAccount, Auth.user_id == UserAccount.id)
        .where(UserAccount.email == email, UserAccount.is_active.is_(True))
    )
    result = await session.execute(stmt)
    result = result.unique().scalar_one_or_none()
    if not result:
        raise exceptions.UnauthorizedException(detail="Invalid email or password")
    return result


async def increment_failed_attempts(session: AsyncSession, auth: Auth) -> Auth:
    """Increment failed login attempts and lock if threshold reached."""
    auth.failed_login_attempts += 1

    if auth.failed_login_attempts >= settings.MAX_FAILED_ATTEMPTS:
        auth.locked_until = datetime.now(timezone.utc) + timedelta(
            minutes=settings.LOCKOUT_DURATION_MINUTES
        )

    await session.flush()
    return auth


async def reset_failed_attempts(session: AsyncSession, auth: Auth) -> Auth:
    """Reset failed login attempts after a successful login."""
    if auth.failed_login_attempts >= 1:
        auth.failed_login_attempts = 0
        auth.locked_until = None
        await session.flush()
    return auth


def check_account_lock(auth: Auth) -> None:
    """Check if the account is currently locked."""
    if auth.locked_until is not None and datetime.now(timezone.utc) < auth.locked_until:
        raise exceptions.UnauthorizedException(
            detail="Account is temporarily locked due to too many failed login attempts"
        )


async def check_password(session: AsyncSession, auth: Auth, password: str):
    if not verify_password(password, auth.password_hash):
        await increment_failed_attempts(session, auth)
        raise exceptions.UnauthorizedException(detail="Invalid email or password")


def validate_refresh_token(refresh_token: str):
    try:
        payload = decode_refresh_token(refresh_token)
    except JWTError:
        raise exceptions.UnauthorizedException(detail="Invalid refresh token")
    if payload is None or payload.get("type") != "refresh":
        raise exceptions.UnauthorizedException(detail="Invalid refresh token")


async def update_password(session: AsyncSession, auth: Auth, new_password: str) -> Auth:
    """Update the password hash."""
    auth.password_hash = hash_password(new_password)
    auth.failed_login_attempts = 0
    auth.locked_until = None
    await session.flush()
    return auth


async def set_recovery_token(session: AsyncSession, auth: Auth) -> str:
    """Generate and set a recovery token with expiration.

    The raw token is returned to be sent via a side-channel (e.g. email).
    Only the SHA-256 hash is stored in the database.
    """
    raw_token = generate_recovery_token()
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    auth.recovery_token = token_hash
    auth.recovery_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    await session.flush()
    return raw_token


async def clear_recovery_token(session: AsyncSession, auth: Auth) -> Auth:
    """Clear the recovery token after use."""
    auth.recovery_token = None
    auth.recovery_token_expires_at = None
    await session.flush()
    return auth


def is_recovery_token_valid(auth: Auth, token: str) -> bool:
    """Validate a recovery token and its expiration.

    Compares the SHA-256 hash of the provided token against the stored hash
    using a timing-safe comparison to prevent timing attacks.
    """
    if auth.recovery_token is None or auth.recovery_token_expires_at is None:
        return False
    if datetime.now(timezone.utc) >= auth.recovery_token_expires_at:
        return False
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return hmac.compare_digest(auth.recovery_token, token_hash)


def generate_credentials(user_id: int, role: str) -> tuple[str, str]:
    access_token = create_access_token(data={"sub": str(user_id), "role": role})
    refresh_token = create_refresh_token(data={"sub": str(user_id)})
    return access_token, refresh_token


def validate_access_token(token: str) -> dtos.AccessTokenPayload:
    """Decode and validate JWT access token, returning payload.

    Args:
        token: Raw JWT access token string

    Returns:
        AccessTokenPayload with user_id (sub), role, and type

    Raises:
        UnauthorizedException: If token is invalid, expired, or malformed
    """
    try:
        payload = decode_token(token)
    except JWTError:
        raise exceptions.UnauthorizedException(detail="Could not validate credentials")

    # Validate token type
    if payload.get("type") != "access":
        raise exceptions.UnauthorizedException(detail="Invalid token type")
    user_id = payload.get("sub")
    role_name = payload.get("role")
    if user_id is None:
        raise exceptions.UnauthorizedException(
            detail="Invalid token payload: missing 'sub'"
        )
    if role_name is None:
        raise exceptions.UnauthorizedException(
            detail="Invalid token payload: missing 'role'"
        )

    return dtos.AccessTokenPayload(
        sub=int(user_id),
        role=role_name,
        type=payload.get("type"),
    )


async def get_user_from_token(
    session: AsyncSession,
    payload: dtos.AccessTokenPayload,
) -> UserAccount:
    """Validate user exists, is active, and role matches token.

    Args:
        session: Database session
        payload: Decoded and validated access token payload

    Returns:
        UserAccount if all validations pass

    Raises:
        UnauthorizedException: If user not found
        ForbiddenException: If user inactive or role mismatch
    """
    auth = await shared_services.get_one_by_field(
        session, Auth, "user_id", payload.sub, include_deleted=False
    )
    if auth is None:
        raise exceptions.UnauthorizedException(detail="User not found")
    if not auth.user.is_active:
        raise exceptions.ForbiddenException(detail="User account is deactivated")
    if auth.user.role is None:
        raise exceptions.ForbiddenException(detail="No role assigned to user")
    return auth.user
