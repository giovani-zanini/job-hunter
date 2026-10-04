"""Dependencies for resources that need a local profile owner."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profile.features.user import handlers as user_handlers
from src.shared.database import sql_client


async def get_anonymous_user_id(
    db_session: AsyncSession = Depends(sql_client.get_sql_default_session),
) -> int:
    user = await user_handlers.resolve_anonymous_user(db_session)
    return user.id
