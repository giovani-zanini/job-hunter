"""Auth use cases: login, change password, recovery."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared import exceptions
from src.shared.database import sql_client
from src.modules.auth.features.account import services as account_services
from src.modules.auth.features.identity import dtos
from src.modules.auth.features.identity import services
from src.modules.auth.features.session import services as session
from src.modules.auth.features.role import services as role
from src.modules.auth.shared.utils import verify_password
from src.modules.auth.shared import dtos as shared_dtos


async def login(
    db_session: AsyncSession,
    data: dtos.LoginRequest,
    ip_address: str,
    user_agent: str,
) -> dtos.TokenResponse:
    """Authenticate user and return JWT token pair."""
    # Find user by email
    auth = await services.get_credentials_by_user_email(db_session, data.email)

    # Check lockout
    services.check_account_lock(auth)

    # Verify password
    await services.check_password(db_session, auth, data.password)

    # Success: reset failed attempts
    await services.reset_failed_attempts(db_session, auth)

    # Generate tokens
    role_record = await role.get_role_by_user_id(
        db_session=db_session, user_id=auth.user_id
    )
    access_token, refresh_token = services.generate_credentials(
        user_id=auth.user_id, role=role_record.name
    )

    # Create session record
    await session.create_session(
        db_session,
        user_id=auth.user_id,
        refresh_token=refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    await db_session.commit()

    return dtos.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def refresh_token(
    db_session: AsyncSession,
    data: dtos.RefreshTokenRequest,
    ip_address: str,
    user_agent: str,
) -> dtos.TokenResponse:
    """Refresh JWT tokens using a valid refresh token."""
    services.validate_refresh_token(data.refresh_token)
    session_record = await session.get_session_by_refresh_token(
        db_session=db_session,
        refresh_token=data.refresh_token,
    )
    await session.revoke_session_by_expiration_date(
        db_session=db_session, session_record=session_record
    )
    await session.revoke_session(db_session, session_record)
    role_record = await role.get_role_by_user_id(
        db_session=db_session, user_id=session_record.user_id
    )
    access_token, refresh_token = services.generate_credentials(
        user_id=session_record.user_id, role=role_record.name
    )
    await session.create_session(
        db_session,
        user_id=session_record.user_id,
        refresh_token=refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return dtos.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# --- Access Token Validation Use Cases ---


async def reset_password(
    session: AsyncSession,
    data: dtos.ResetPasswordRequest,
) -> None:
    """Reset password using a recovery token."""
    user = await account_services.get_user_by_email(session, data.email)
    if not user:
        raise exceptions.UnauthorizedException(detail="Invalid recovery token")

    auth = await services.get_auth_by_user_id(session, user.id)
    if not auth:
        raise exceptions.UnauthorizedException(detail="Invalid recovery token")

    if not services.is_recovery_token_valid(auth, data.recovery_token):
        raise exceptions.UnauthorizedException(
            detail="Invalid or expired recovery token"
        )

    await services.update_password(session, auth, data.new_password)
    await services.clear_recovery_token(session, auth)


async def request_recovery(
    session: AsyncSession,
    data: dtos.RequestRecoveryRequest,
) -> dtos.RecoveryTokenResponse:
    """Request a password recovery token."""
    user = await account_services.get_user_by_email(session, data.email)
    if not user:
        # Return generic message to avoid email enumeration
        return dtos.RecoveryTokenResponse(
            message="If the email exists, a recovery token has been sent via email",
        )

    auth = await services.get_auth_by_user_id(session, user.id)
    if not auth:
        return dtos.RecoveryTokenResponse(
            message="If the email exists, a recovery token has been sent via email",
        )

    token = await services.set_recovery_token(session, auth)

    # NOTE: In production, send `token` via email instead of logging/returning it.
    # The raw token is intentionally NOT included in the HTTP response.
    return dtos.RecoveryTokenResponse(
        message="If the email exists, a recovery token has been sent via email",
    )


async def change_password(
    session: AsyncSession,
    user_id: int,
    data: dtos.ChangePasswordRequest,
) -> None:
    """Change password for the authenticated user."""
    auth = await services.get_auth_by_user_id(session, user_id)
    if not auth:
        raise exceptions.NotFoundException(detail="Auth record not found")

    if not verify_password(data.current_password, auth.password_hash):
        raise exceptions.UnauthorizedException(detail="Current password is incorrect")

    await services.update_password(session, auth, data.new_password)


async def get_current_user(
    db_session: AsyncSession,
    token: str,
) -> shared_dtos.AuthenticatedUser:
    """Extract and validate the JWT access token, returning the authenticated User.

    This dependency orchestrates three validation layers:
    1. Token validation: decode JWT and extract payload
    2. Identity validation: verify user exists, is active, and role is assigned
    3. Role consistency: compare token role claim against current DB role.
       If they diverge (role changed in DB), all sessions are revoked and the
       user must re-authenticate.

    Returns:
        AuthenticatedUser: Lightweight identity DTO

    Raises:
        UnauthorizedException: Invalid token, user not found, or role mismatch
        ForbiddenException: User inactive or no role assigned
    """
    payload = services.validate_access_token(token)
    user = await services.get_user_from_token(db_session, payload)

    # Detect role mismatch between token claim and current DB value
    if user.role.name != payload.role:
        async with sql_client.get_session("write") as write_session:
            await session.revoke_all_user_sessions(write_session, user.id)
        raise exceptions.UnauthorizedException(
            detail="Role has been changed. Please log in again."
        )

    return shared_dtos.AuthenticatedUser(
        id=user.id,
        email=user.email,
        role_name=user.role.name,
        is_active=user.is_active,
    )
