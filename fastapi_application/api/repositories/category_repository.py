import logging
from uuid import UUID

from fastapi_pagination import Params, Page
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastapi_application.core.models import Category
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


class SQLAlchemyCategoryRepository(BaseRepository[Category]):

    async def get(
        self,
        session: AsyncSession,
        obj_id: UUID,
    ) -> Category | None:
        return await get_handler(
            Category,
            session,
            obj_id,
        )

    async def get_all(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Category]:
        return await get_all_handler(
            Category,
            session,
            limit,
            offset,
        )

    async def get_many(
        self,
        session: AsyncSession,
        obj_ids: list[UUID],
    ) -> list[Category]:
        return await get_many_handler(
            Category,
            session,
            obj_ids,
        )

    async def get_multi_paginated(
        self,
        session: AsyncSession,
        params: Params,
    ) -> Page[Category]:
        return await get_multi_paginated_handler(
            Category,
            session,
            params,
        )

    async def create(
        self,
        session: AsyncSession,
        obj_data: dict,
    ) -> Category:
        return await create_handler(
            Category,
            session,
            obj_data,
        )

    async def update_partial(
        self,
        session: AsyncSession,
        obj: Category,
        obj_upd: dict,
    ) -> Category:
        return await update_partial_handler(
            session,
            obj,
            obj_upd,
        )

    async def delete(
        self,
        session: AsyncSession,
        obj: Category,
    ) -> None:
        await delete_handler(
            session,
            obj,
        )

    async def get_with_products(
        self,
        session: AsyncSession,
        obj_id: UUID,
    ) -> Category | None:
        query = (
            select(Category)
            .options(selectinload(Category.products))
            .where(Category.id == obj_id)
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_name(
        self,
        session: AsyncSession,
        category_name: str,
    ) -> Category | None:
        query = select(Category).where(Category.name == category_name)
        result: Result = await session.execute(query)
        category = result.scalar_one_or_none()
        return category
