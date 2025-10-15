import logging
from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_application.core.models import Order
from fastapi_application.core.schemas.order_schema import (
    OrderCreateWithProducts,
    OrderUpdateWithProducts,
    OrderUpdateWithProductsPartial,
    OrderCreate,
    OrderUpdate,
    OrderUpdatePartial,
)
from fastapi_application.api.repositories.order_repository import (
    SQLAlchemyOrderRepository,
)
from fastapi_application.api.repositories.product_repository import (
    SQLAlchemyProductRepository,
)


logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        order_repo: SQLAlchemyOrderRepository,
        product_repo: SQLAlchemyProductRepository,
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo

    async def create_order(
        self,
        session: AsyncSession,
        order_data: OrderCreate,
    ) -> Order:
        order_dict = order_data.model_dump()
        return await self.order_repo.create(
            session,
            order_dict,
        )

    async def get_order(
        self,
        session: AsyncSession,
        order_id: UUID,
    ) -> Order:
        order = await self.order_repo.get(
            session,
            order_id,
        )
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    async def get_all_orders(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        with_assoc: bool = False,
    ) -> list[Order]:
        return await self.order_repo.get_all(
            session,
            limit,
            offset,
            with_assoc,
        )

    async def get_many_orders(
        self,
        session: AsyncSession,
        order_ids: list[UUID],
        with_assoc: bool = False,
    ) -> list[Order]:
        return await self.order_repo.get_many(
            session,
            order_ids,
            with_assoc,
        )

    async def get_orders_with_paginated(
        self,
        session: AsyncSession,
        params: Params | None = None,
    ) -> Page[Order]:
        return await self.order_repo.get_multi_paginated(
            session,
            params,
        )

    async def update_orders_partial(
        self,
        session: AsyncSession,
        order: Order,
        order_upd: OrderUpdate | OrderUpdatePartial,
        partial: bool = False,
    ) -> Order:
        order_dict = order_upd.model_dump(exclude_unset=partial)
        return await self.order_repo.update_partial(
            session,
            order,
            order_dict,
        )

    async def delete_order(
        self,
        session: AsyncSession,
        order: Order,
    ) -> None:
        return await self.order_repo.delete(
            session,
            order,
        )

    async def create_order_with_products(
        self,
        session: AsyncSession,
        order_data: OrderCreateWithProducts,
    ) -> Order:
        logger.info(
            "Create order requested",
            extra={
                "order for user": order_data.user_id,
                "promo": (
                    str(order_data.promo_code) if order_data.promo_code else None
                ),
                "products of order": order_data.products,
            },
        )

        order_dict = order_data.model_dump()

        result = await self.product_repo.get_many(
            session, [item.product_id for item in order_data.products]
        )

        products = {p.id: p for p in result}
        order = await self.order_repo.create_order_with_products(
            session, order_dict, products
        )
        logger.info("Order created", extra={"order_id": str(order.id)})
        return order

    async def update_order_with_products_partial(
        self,
        session: AsyncSession,
        order: Order,
        order_upd: OrderUpdateWithProducts | OrderUpdateWithProductsPartial,
        partial: bool = False,
    ) -> Order:
        data = order_upd.model_dump(exclude_unset=partial)
        product_ids = [p["product_id"] for p in data.get("products_data", [])]
        result = await self.product_repo.get_many(session, product_ids)
        products = {p.id: p for p in result}
        data["products"] = products

        return await self.order_repo.update_partial_with_products(
            session,
            order,
            data,
        )
