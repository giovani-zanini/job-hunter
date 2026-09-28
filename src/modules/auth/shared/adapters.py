"""FastAPI dependencies for authentication and authorization."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.database import sql_client
from src.shared import exceptions
from src.modules.auth.features.identity import handlers
from src.modules.auth.shared import dtos


_bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db_session: AsyncSession = Depends(sql_client.get_sql_read_session),
) -> dtos.AuthenticatedUser:
    token = credentials.credentials
    return await handlers.get_current_user(db_session, token)


def require_role(roles: list[str]):
    async def _check_role(
        current_user: dtos.AuthenticatedUser = Depends(get_current_user),
    ) -> None:
        if current_user.role_name not in roles:
            raise exceptions.ForbiddenException(
                detail="Forbidden: user does not have the required role to perform this action."
            )

    return _check_role
