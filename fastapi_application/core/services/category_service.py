import structlog
from uuid import UUID
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_application.core.models import Category
from fastapi_application.core.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryUpdatePartial,
)
from fastapi_application.core.services.utils import handle_integrity_error, get_or_404
from fastapi_application.core.repositories.category_repository import (
    SQLAlchemyCategoryRepository,
)

logger = structlog.get_logger(__name__)


class CategoryService:
    def __init__(self, category_repo: SQLAlchemyCategoryRepository) -> None:
        self.category_repo = category_repo

    async def create_category(
        self,
        session: AsyncSession,
        category_data: CategoryCreate,
    ) -> Category:
        logger.info(
            "Creating category",
            category_name=category_data.name,
        )

        category_dict = category_data.model_dump()

        category = await handle_integrity_error(
            self.category_repo.create,
            session,
            category_dict,
            message="Category with that name already exists",
        )

        logger.info(
            "Category created successfully",
            category_id=str(category.id),
            category_name=category.name,
        )
        return category

    async def get_category(
        self,
        session: AsyncSession,
        category_id: UUID,
    ) -> Category:
        logger.debug("Fetching category", category_id=str(category_id))
        category = await self.category_repo.get(session, category_id)
        get_or_404(category)
        logger.debug("Category fetched successfully", category_id=str(category_id))
        return category

    async def get_all_categories(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Category]:
        logger.debug("Fetching all categories", limit=limit, offset=offset)
        categories = await self.category_repo.get_all(session, limit, offset)
        logger.debug("Fetched categories", count=len(categories))
        return categories

    async def get_many_categories(
        self,
        session: AsyncSession,
        category_ids: list[UUID],
    ) -> list[Category]:
        logger.debug(
            "Fetching multiple categories",
            category_ids=[str(cid) for cid in category_ids],
        )
        categories = await self.category_repo.get_many(session, category_ids)
        logger.debug("Fetched multiple categories", count=len(categories))
        return categories

    async def get_categories_with_paginated(
        self,
        session: AsyncSession,
        params: Params | None = None,
    ) -> Page[Category]:
        logger.debug(
            "Fetching paginated categories",
            params=params.model_dump() if params else None,
        )
        page = await self.category_repo.get_multi_paginated(session, params=params)
        logger.debug("Paginated categories fetched", total=len(page.items))
        return page

    async def update_category_with_partial(
        self,
        session: AsyncSession,
        category: Category,
        category_upd: CategoryUpdate | CategoryUpdatePartial,
        partial: bool = False,
    ) -> Category:
        logger.info(
            "Updating category",
            category_id=str(category.id),
            partial_update=partial,
        )

        category_dict = category_upd.model_dump(exclude_unset=partial)
        updated_category = await handle_integrity_error(
            self.category_repo.update_partial,
            session,
            category,
            category_dict,
            message="Category with that name already exists",
        )

        logger.info(
            "Category updated successfully",
            category_id=str(category.id),
        )
        return updated_category

    async def delete_category(
        self,
        session: AsyncSession,
        category: Category,
    ) -> None:
        logger.warning("Deleting category", category_id=str(category.id))
        await self.category_repo.delete(session, category)
        logger.info("Category deleted", category_id=str(category.id))

    async def get_category_with_products(
        self,
        session: AsyncSession,
        category_id: UUID,
    ) -> Category:
        logger.debug("Fetching category with products", category_id=str(category_id))
        category = await self.category_repo.get_with_products(session, category_id)
        get_or_404(category)
        logger.debug(
            "Fetched category with products",
            category_id=str(category.id),
            product_count=len(category.products) if category.products else 0,
        )
        return category
