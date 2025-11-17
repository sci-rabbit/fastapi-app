import structlog
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

logger = structlog.get_logger(__name__)


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
        user_id = str(order_data.user_id) if order_data.user_id else None
        logger.info("Creating order", user_id=user_id, promo_code=order_data.promo_code)

        try:
            order_dict = order_data.model_dump()
            order = await self.order_repo.create(session, order_dict)

            logger.info(
                "Order created successfully",
                order_id=str(order.id),
                user_id=user_id,
            )
            return order

        except Exception as e:
            logger.error(
                "Failed to create order",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise

    async def create_order_with_products(
        self,
        session: AsyncSession,
        order_data: OrderCreateWithProducts,
    ) -> Order:
        user_id = str(order_data.user_id) if order_data.user_id else None
        product_ids = [str(p.product_id) for p in order_data.products]

        logger.info(
            "Creating order with products",
            user_id=user_id,
            promo_code=order_data.promo_code,
            products_count=len(product_ids),
            product_ids=product_ids,
        )

        try:
            order_dict = order_data.model_dump()

            logger.debug("Fetching product references", product_ids=product_ids)
            result = await self.product_repo.get_many(
                session, [item.product_id for item in order_data.products]
            )
            products = {p.id: p for p in result}

            logger.debug(
                "Products fetched",
                found_count=len(products),
                requested_count=len(order_data.products),
            )

            order = await self.order_repo.create_order_with_products(
                session, order_dict, products
            )

            logger.info(
                "Order with products created successfully",
                order_id=str(order.id),
                user_id=user_id,
                products_count=len(products),
            )
            return order

        except Exception as e:
            logger.error(
                "Failed to create order with products",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise


    async def get_order(
        self,
        session: AsyncSession,
        order_id: UUID,
    ) -> Order:
        logger.debug("Fetching order", order_id=str(order_id))

        order = await self.order_repo.get(session, order_id)
        if not order:
            logger.warning("Order not found", order_id=str(order_id))
            raise HTTPException(status_code=404, detail="Order not found")

        logger.debug("Order fetched successfully", order_id=str(order.id))
        return order

    async def get_all_orders(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        with_assoc: bool = False,
    ) -> list[Order]:
        logger.debug(
            "Fetching all orders", limit=limit, offset=offset, with_assoc=with_assoc
        )
        orders = await self.order_repo.get_all(session, limit, offset, with_assoc)
        logger.debug("Orders fetched", count=len(orders))
        return orders

    async def get_many_orders(
        self,
        session: AsyncSession,
        order_ids: list[UUID],
        with_assoc: bool = False,
    ) -> list[Order]:
        logger.debug(
            "Fetching multiple orders",
            order_ids=[str(oid) for oid in order_ids],
            with_assoc=with_assoc,
        )
        orders = await self.order_repo.get_many(session, order_ids, with_assoc)
        logger.debug("Fetched multiple orders", count=len(orders))
        return orders

    async def get_orders_with_paginated(
        self,
        session: AsyncSession,
        params: Params | None = None,
    ) -> Page[Order]:
        logger.debug(
            "Fetching paginated orders", params=params.model_dump() if params else None
        )
        page = await self.order_repo.get_multi_paginated(session, params)
        logger.debug("Paginated orders fetched", total=len(page.items))
        return page


    async def update_orders_partial(
        self,
        session: AsyncSession,
        order: Order,
        order_upd: OrderUpdate | OrderUpdatePartial,
        partial: bool = False,
    ) -> Order:
        logger.info("Updating order", order_id=str(order.id), partial_update=partial)
        order_dict = order_upd.model_dump(exclude_unset=partial)
        updated = await self.order_repo.update_partial(session, order, order_dict)
        logger.info("Order updated successfully", order_id=str(order.id))
        return updated

    async def update_order_with_products_partial(
        self,
        session: AsyncSession,
        order: Order,
        order_upd: OrderUpdateWithProducts | OrderUpdateWithProductsPartial,
        partial: bool = False,
    ) -> Order:
        logger.info(
            "Updating order with products",
            order_id=str(order.id),
            partial_update=partial,
        )

        data = order_upd.model_dump(exclude_unset=partial)
        product_ids = [p["product_id"] for p in data.get("products_data", [])]

        logger.debug("Fetching related products for update", product_ids=product_ids)
        result = await self.product_repo.get_many(session, product_ids)
        products = {p.id: p for p in result}
        data["products"] = products

        updated_order = await self.order_repo.update_partial_with_products(
            session,
            order,
            data,
        )

        logger.info(
            "Order with products updated successfully",
            order_id=str(order.id),
            updated_products=len(products),
        )
        return updated_order


    async def delete_order(
        self,
        session: AsyncSession,
        order: Order,
    ) -> None:
        logger.warning("Deleting order", order_id=str(order.id))
        await self.order_repo.delete(session, order)
        logger.info("Order deleted successfully", order_id=str(order.id))
