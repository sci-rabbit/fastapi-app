import logging
from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

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


logger = logging.getLogger(__name__)


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
            "Create product requested",
            extra={
                "name": product_data.name,
                "category_name": (
                    str(product_data.category_name)
                    if product_data.category_name
                    else None
                ),
            },
        )

        category_id: UUID | None = None
        if product_data.category_name is not None:
            category = await self.category_repo.get_by_name(
                session, product_data.category_name
            )
            if category is None:
                raise HTTPException(status_code=404, detail="Category not found")
            category_id = category.id

        product = await self.product_repo.create(
            session,
            {
                "name": product_data.name,
                "price": product_data.price,
                "category_id": category_id,
            },
        )
        logger.info("Product created", extra={"product_id": str(product.id)})
        return product

    async def get_product(
        self,
        session: AsyncSession,
        product_id: UUID,
    ) -> Product:
        product = await self.product_repo.get(session, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    async def get_all_products(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Product]:
        return await self.product_repo.get_all(
            session,
            limit,
            offset,
        )

    async def get_many_products(
        self,
        session: AsyncSession,
        product_ids: list[UUID],
    ) -> list[Product]:
        return await self.product_repo.get_many(
            session,
            product_ids,
        )

    async def get_products_with_paginated(
        self,
        session: AsyncSession,
        params: Params | None = None,
    ) -> Page[Product]:
        return await self.product_repo.get_multi_paginated(
            session,
            params=params,
        )

    async def update_product_with_partial(
        self,
        session: AsyncSession,
        product: Product,
        product_upd: ProductUpdate | ProductUpdatePartial,
        partial: bool = False,
    ) -> Product:

        product_dict = product_upd.model_dump(exclude_unset=partial)

        category_id: UUID | None = None
        if product_dict.get("category_name") is not None:
            category = await self.category_repo.get_by_name(
                session, product_dict.get("category_name")
            )
            if category is None:
                raise HTTPException(status_code=404, detail="Category not found")
            category_id = category.id

        product_dict["category_id"] = category_id
        product_dict.pop("category_name", None)

        return await self.product_repo.update_partial(
            session,
            product,
            product_dict,
        )

    async def delete_product(
        self,
        session: AsyncSession,
        product: Product,
    ) -> None:
        await self.product_repo.delete(
            session,
            product,
        )
