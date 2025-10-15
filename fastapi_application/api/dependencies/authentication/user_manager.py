from typing import Annotated, TYPE_CHECKING

from fastapi import Depends

from fastapi_application.api.dependencies.authentication.get_dbs import get_user_db
from fastapi_application.core.authentication.user_manager import UserManager

if TYPE_CHECKING:
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase


async def get_user_manager(
    users_db: Annotated[
        "SQLAlchemyUserDatabase",
        Depends(get_user_db),
    ],
):
    yield UserManager(
        users_db,
    )
