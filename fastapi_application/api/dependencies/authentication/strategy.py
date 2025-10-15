from typing import (
    TYPE_CHECKING,
    Annotated,
)

from fastapi import Depends
from fastapi_users.authentication.strategy.db import (
    DatabaseStrategy,
)

from fastapi_application.api.dependencies.authentication.get_dbs import get_access_token_db
from fastapi_application.core.config import settings
from fastapi_application.core.models.access_token import AccessToken

if TYPE_CHECKING:

    from fastapi_users.authentication.strategy.db import AccessTokenDatabase


def get_database_strategy(
    access_tokens_db: Annotated[
        "AccessTokenDatabase[AccessToken]",
        Depends(get_access_token_db),
    ],
) -> DatabaseStrategy:
    return DatabaseStrategy(
        database=access_tokens_db,
        lifetime_seconds=settings.access_token.lifetime_seconds,
    )
