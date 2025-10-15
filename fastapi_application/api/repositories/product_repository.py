import logging
from uuid import UUID

from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_application.core.models import Product
from fastapi_application.api.repositories.base_repository import BaseRepository
from fastapi_application.api.repositories.utils import (
    get_all_handler,
    get_handler,
    get_many_handler,
    get_multi_paginated_handler,
    update_partial_handler,
    delete_handler,
    create_handler,
)

logger = logging.getLogger(__name__)


class SQLAlchemyProductRepository(BaseRepository[Product]):

    async def get(
        self,
        session: AsyncSession,
        obj_id: UUID,
    ) -> Product | None:
        return await get_handler(
            Product,
            session,
            obj_id,
        )

    async def get_all(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Product]:
        return await get_all_handler(
            Product,
            session,
            limit,
            offset,
        )

    async def get_many(
        self,
        session: AsyncSession,
        obj_ids: list[UUID],
    ) -> list[Product]:
        return await get_many_handler(
            Product,
            session,
            obj_ids,
        )

    async def get_multi_paginated(
        self,
        session: AsyncSession,
        params: Params,
    ) -> Page[Product]:
        return await get_multi_paginated_handler(
            Product,
            session,
            params,
        )

    async def create(
        self,
        session: AsyncSession,
        obj_data: dict,
    ) -> Product:
        return await create_handler(
            Product,
            session,
            obj_data,
        )

    async def update_partial(
        self,
        session: AsyncSession,
        obj: Product,
        obj_upd: dict,
    ) -> Product:
        return await update_partial_handler(
            session,
            obj,
            obj_upd,
        )

    async def delete(
        self,
        session: AsyncSession,
        obj: Product,
    ) -> None:
        await delete_handler(
            session,
            obj,
        )
