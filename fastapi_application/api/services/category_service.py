import logging
from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_application.core.models import Category
from fastapi_application.core.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryUpdatePartial,
)
from fastapi_application.api.services.utils import handle_integrity_error
from fastapi_application.api.repositories.category_repository import (
    SQLAlchemyCategoryRepository,
)

logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(
        self,
        category_repo: SQLAlchemyCategoryRepository,
    ) -> None:
        self.category_repo = category_repo

    async def create_category(
        self,
        session: AsyncSession,
        category_data: CategoryCreate,
    ):
        logger.info(
            "Create category requested",
            extra={
                "category_name": (str(category_data.name)),
            },
        )

        category_dict = category_data.model_dump()

        category = await handle_integrity_error(
            self.category_repo.create,
            session,
            category_dict,
            message="Category with that name already exists",
        )

        logger.info("Category created", extra={"category_id": str(category.id)})
        return category

    async def get_category(
        self,
        session: AsyncSession,
        category_id: UUID,
    ) -> Category:
        category = await self.category_repo.get(session, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    async def get_all_categories(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Category]:
        return await self.category_repo.get_all(
            session,
            limit,
            offset,
        )

    async def get_many_categories(
        self,
        session: AsyncSession,
        category_ids: list[UUID],
    ) -> list[Category]:
        return await self.category_repo.get_many(
            session,
            category_ids,
        )

    async def get_categories_with_paginated(
        self,
        session: AsyncSession,
        params: Params | None = None,
    ) -> Page[Category]:
        return await self.category_repo.get_multi_paginated(session, params=params)

    async def update_category_with_partial(
        self,
        session: AsyncSession,
        category: Category,
        category_upd: CategoryUpdate | CategoryUpdatePartial,
        partial: bool = False,
    ) -> Category:
        category_dict = category_upd.model_dump(exclude_unset=partial)
        return await handle_integrity_error(
            self.category_repo.update_partial,
            session,
            category,
            category_dict,
            message="Category with that name already exists",
        )

    async def delete_category(
        self,
        session: AsyncSession,
        category: Category,
    ) -> None:
        await self.category_repo.delete(
            session,
            category,
        )

    async def get_category_with_products(
        self,
        session: AsyncSession,
        category_id: UUID,
    ) -> Category:
        category = await self.category_repo.get_with_products(
            session,
            category_id,
        )
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
