import logging
from uuid import UUID

from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_application.core.models import Post
from fastapi_application.core.repositories.base_repository import BaseRepository
from fastapi_application.core.repositories.utils import (
    get_all_handler,
    get_handler,
    get_many_handler,
    get_multi_paginated_handler,
    update_partial_handler,
    delete_handler,
    create_handler,
)

logger = logging.getLogger(__name__)


class SQLAlchemyPostRepository(BaseRepository[Post]):

    async def get(
        self,
        session: AsyncSession,
        obj_id: UUID,
    ) -> Post | None:
        return await get_handler(
            Post,
            session,
            obj_id,
        )

    async def get_all(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Post]:
        return await get_all_handler(
            Post,
            session,
            limit,
            offset,
        )

    async def get_many(
        self,
        session: AsyncSession,
        obj_ids: list[UUID],
    ) -> list[Post]:
        return await get_many_handler(
            Post,
            session,
            obj_ids,
        )

    async def get_multi_paginated(
        self,
        session: AsyncSession,
        params: Params,
    ) -> Page[Post]:
        return await get_multi_paginated_handler(
            Post,
            session,
            params,
        )

    async def create(
        self,
        session: AsyncSession,
        obj_data: dict,
    ) -> Post:
        return await create_handler(
            Post,
            session,
            obj_data,
        )

    async def update_partial(
        self,
        session: AsyncSession,
        obj: Post,
        obj_upd: dict,
    ) -> Post:
        return await update_partial_handler(
            session,
            obj,
            obj_upd,
        )

    async def delete(
        self,
        session: AsyncSession,
        obj: Post,
    ) -> None:
        await delete_handler(
            session,
            obj,
        )
