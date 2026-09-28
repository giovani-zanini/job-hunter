"""User feature router with CRUD endpoints (auth module)."""

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.shared import adapters
from src.modules.auth.features.account.models import UserAccount
from src.modules.auth.features.account import dtos
from src.modules.auth.features.account import handlers
from src.shared.database import sql_client
from src.modules.auth.shared import dtos as shared_dtos


bearer_scheme = HTTPBearer()
router = APIRouter(prefix="/account", tags=["Account"])


@router.post(
    "/",
    response_model=dtos.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    data: dtos.UserCreateRequest,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> dtos.UserResponse:
    """Create a new user with authentication credentials."""
    return await handlers.create_user(session, data)


@router.get(
    "/me",
    response_model=dtos.UserResponse,
    summary="Get current user",
)
async def get_user(
    session: AsyncSession = Depends(sql_client.get_sql_read_session),
    user: shared_dtos.AuthenticatedUser = Depends(adapters.get_current_user),
) -> dtos.UserResponse:
    """Get the authenticated user's information."""
    return await handlers.get_user(session, user.id)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user",
)
async def delete_user(
    request: Request,
    session: AsyncSession = Depends(sql_client.get_sql_default_session),
    user: shared_dtos.AuthenticatedUser = Depends(adapters.get_current_user),
) -> None:
    """Delete the authenticated user's account permanently."""
    # user_id is injected by AuthorizationMiddleware
    await handlers.delete_user(session, user.id)
