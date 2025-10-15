from typing import TYPE_CHECKING

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase

from fastapi_application.core.db import get_session
from fastapi_application.core.models import User, AccessToken

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_access_token_db(session: "AsyncSession" = Depends(get_session)):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


async def get_user_db(session: "AsyncSession" = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)
