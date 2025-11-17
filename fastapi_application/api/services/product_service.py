import structlog
from uuid import UUID

from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_application.api.services.utils import get_or_404
from fastapi_application.core.models import Product
from fastapi_application.core.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductUpdatePartial,
)
from fastapi_application.api.repositories.category_repository import (
    SQLAlchemyCategoryRepository,
)
from fastapi_application.api.repositories.product_repository import (
    SQLAlchemyProductRepository,
)

logger = structlog.get_logger()


class ProductService:
    def __init__(
        self,
        product_repo: SQLAlchemyProductRepository,
        category_repo: SQLAlchemyCategoryRepository,
    ) -> None:
        self.product_repo = product_repo
        self.category_repo = category_repo

    async def create_product(
        self,
        session: AsyncSession,
        product_data: ProductCreate,
    ) -> Product:
        logger.info(
            "Creating product",
            name=product_data.name,
            price=product_data.price,
            category_name=product_data.category_name,
        )

        try:
            category_id: UUID | None = None
            if product_data.category_name is not None:
                logger.info(
                    "Fetching category by name",
                    category_name=product_data.category_name,
                )
                category = await self.category_repo.get_by_name(
                    session, product_data.category_name
                )
                get_or_404(category)
                category_id = category.id
                logger.info(
                    "Category found",
                    category_name=product_data.category_name,
                    category_id=str(category_id),
                )

            product = await self.product_repo.create(
                session,
                {
                    "name": product_data.name,
                    "price": product_data.price,
                    "category_id": category_id,
                },
            )

            logger.info(
                "Product created successfully",
                product_id=str(product.id),
                name=product_data.name,
                price=product_data.price,
                category_id=str(category_id) if category_id else None,
            )
            return product

        except Exception as e:
            logger.error(
                "Failed to create product",
                name=product_data.name,
                category_name=product_data.category_name,
                error=str(e),
                exc_info=True,
            )
            raise

    async def get_product(
        self,
        session: AsyncSession,
        product_id: UUID,
    ) -> Product:
        logger.info("Getting product", product_id=str(product_id))

        product = await self.product_repo.get(session, product_id)
        if not product:
            logger.warning("Product not found", product_id=str(product_id))
        get_or_404(product)

        logger.info("Product retrieved successfully", product_id=str(product_id))
        return product

    async def get_all_products(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Product]:
        logger.info("Retrieving all products", limit=limit, offset=offset)

        products = await self.product_repo.get_all(session, limit, offset)

        logger.info(
            "Products retrieved successfully",
            count=len(products),
            limit=limit,
            offset=offset,
        )
        return products

    async def get_many_products(
        self,
        session: AsyncSession,
        product_ids: list[UUID],
    ) -> list[Product]:
        logger.info(
            "Retrieving multiple products",
            product_ids=[str(pid) for pid in product_ids],
        )

        products = await self.product_repo.get_many(session, product_ids)

        logger.info(
            "Multiple products retrieved successfully",
            retrieved_count=len(products),
        )
        return products

    async def get_products_with_paginated(
        self,
        session: AsyncSession,
        params: Params | None = None,
    ) -> Page[Product]:
        logger.info("Retrieving paginated products")

        page = await self.product_repo.get_multi_paginated(session, params=params)

        logger.info("Paginated products retrieved", total_items=page.total)
        return page

    async def update_product_with_partial(
        self,
        session: AsyncSession,
        product: Product,
        product_upd: ProductUpdate | ProductUpdatePartial,
        partial: bool = False,
    ) -> Product:
        logger.info(
            "Updating product",
            product_id=str(product.id),
            partial=partial,
        )

        try:
            product_dict = product_upd.model_dump(exclude_unset=partial)

            category_id: UUID | None = None
            if product_dict.get("category_name") is not None:
                logger.info(
                    "Fetching category for update",
                    category_name=product_dict.get("category_name"),
                )
                category = await self.category_repo.get_by_name(
                    session, product_dict.get("category_name")
                )
                get_or_404(category)
                category_id = category.id
                logger.info(
                    "Category found for update",
                    category_name=product_dict.get("category_name"),
                    category_id=str(category_id),
                )

            product_dict["category_id"] = category_id
            product_dict.pop("category_name", None)

            updated_product = await self.product_repo.update_partial(
                session,
                product,
                product_dict,
            )

            logger.info(
                "Product updated successfully",
                product_id=str(updated_product.id),
                partial=partial,
            )
            return updated_product

        except Exception as e:
            logger.error(
                "Failed to update product",
                product_id=str(product.id),
                error=str(e),
                exc_info=True,
            )
            raise

    async def delete_product(
        self,
        session: AsyncSession,
        product: Product,
    ) -> None:
        logger.info("Deleting product", product_id=str(product.id))

        await self.product_repo.delete(session, product)

        logger.info("Product deleted successfully", product_id=str(product.id))
