"""Auth feature router: login, change password, recovery."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.features.identity import dtos
from src.modules.auth.features.identity import handlers
from src.modules.auth.shared.adapters import get_current_user
from src.modules.auth.shared.dtos import AuthenticatedUser
from src.shared.database import sql_client

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/token",
    response_model=dtos.TokenResponse,
    summary="Login and obtain JWT tokens",
)
async def login(
    data: dtos.LoginRequest,
    request: Request,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.TokenResponse:
    """Authenticate with email and password, returns access + refresh tokens."""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    return await handlers.login(
        session, data, ip_address=ip_address, user_agent=user_agent
    )


@router.post(
    "/refresh-token",
    response_model=dtos.TokenResponse,
    summary="Refresh JWT tokens",
)
async def refresh_token(
    data: dtos.RefreshTokenRequest,
    request: Request,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.TokenResponse:
    """Refresh access and refresh tokens using a valid refresh token (rotation)."""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    return await handlers.refresh_token(
        session, data, ip_address=ip_address, user_agent=user_agent
    )


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password for the authenticated user",
)
async def change_password(
    data: dtos.ChangePasswordRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> None:
    """Change the password for the currently authenticated user."""
    await handlers.change_password(session, current_user.id, data)


@router.post(
    "/request-recovery",
    response_model=dtos.RecoveryTokenResponse,
    summary="Request a password recovery token",
)
async def request_recovery(
    data: dtos.RequestRecoveryRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.RecoveryTokenResponse:
    """Request a recovery token for password reset."""
    return await handlers.request_recovery(session, data)


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reset password using recovery token",
)
async def reset_password(
    data: dtos.ResetPasswordRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> None:
    """Reset password using a valid recovery token."""
    await handlers.reset_password(session, data)
