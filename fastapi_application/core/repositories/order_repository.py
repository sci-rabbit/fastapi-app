import logging
from uuid import UUID

from fastapi_pagination import Params, Page
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.engine import Result

from fastapi_application.core.models import Order, OrderProductAssociation, Product
from fastapi_application.core.repositories.base_repository import BaseRepository
from fastapi_application.core.repositories.utils import (
    get_handler,
    get_multi_paginated_handler,
    update_partial_handler,
    delete_handler,
    create_handler,
)

logger = logging.getLogger(__name__)


class SQLAlchemyOrderRepository(BaseRepository[Order]):

    async def get(
        self,
        session: AsyncSession,
        obj_id: UUID,
    ) -> Order | None:
        return await get_handler(
            Order,
            session,
            obj_id,
        )

    async def get_all(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        with_assoc: bool = False,
    ) -> list[Order]:
        if with_assoc:
            query = (
                select(Order)
                .options(
                    selectinload(Order.products_details).selectinload(
                        OrderProductAssociation.product
                    )
                )
                .limit(limit)
                .offset(offset)
            )
        else:
            query = select(Order).limit(limit).offset(offset)

        res: Result = await session.execute(query)
        return list(res.scalars().all())

    async def get_many(
        self,
        session: AsyncSession,
        obj_ids: list[UUID],
        with_assoc: bool = False,
    ) -> list[Order]:
        if not obj_ids:
            return []

        if with_assoc:
            query = (
                select(Order)
                .options(
                    selectinload(Order.products_details).selectinload(
                        OrderProductAssociation.product
                    )
                )
                .where(Order.id.in_(obj_ids))
            )
        else:
            query = select(Order).where(Order.id.in_(obj_ids))
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_multi_paginated(
        self,
        session: AsyncSession,
        params: Params,
    ) -> Page[Order]:
        return await get_multi_paginated_handler(
            Order,
            session,
            params,
        )

    async def create(
        self,
        session: AsyncSession,
        obj_data: dict,
    ) -> Order:
        return await create_handler(
            Order,
            session,
            obj_data,
        )

    async def update_partial(
        self,
        session: AsyncSession,
        obj: Order,
        obj_upd: dict,
    ) -> Order:
        return await update_partial_handler(
            session,
            obj,
            obj_upd,
        )

    async def delete(
        self,
        session: AsyncSession,
        obj: Order,
    ) -> None:
        await delete_handler(
            session,
            obj,
        )

    async def create_order_with_products(
        self,
        session: AsyncSession,
        obj_data: dict,
        products: dict[UUID, Product],
    ) -> Order | None:
        order_data = obj_data.copy()
        order_data.pop("products")
        order = Order(**order_data)

        session.add(order)
        await session.flush()

        for item in obj_data.get("products", []):
            product_inst = products.get(item.get("product_id"))
            if not product_inst:
                raise ValueError(
                    f"Product with id {item.get("product_id")} does not exist"
                )
            assoc = OrderProductAssociation(
                order_id=order.id,
                product_id=item.get("product_id"),
                count=item.get("count"),
                unit_price=product_inst.price,
            )
            session.add(assoc)

        await session.flush()
        return order

    async def update_partial_with_products(
        self,
        session: AsyncSession,
        obj: Order,
        obj_upd: dict,
    ) -> Order:
        for name, value in obj_upd.items():
            if name != "products_data" and name != "products":
                setattr(obj, name, value)

        for upd_product in obj_upd.get("products_data", []):
            assoc = next(
                (
                    p
                    for p in obj.products_details
                    if p.product_id == upd_product["product_id"]
                ),
                None,
            )
            product_inst = obj_upd.get("products", {}).get(upd_product["product_id"])
            if not product_inst:
                raise ValueError(f"Product {upd_product['product_id']} not found")

            if assoc:
                assoc.count = upd_product.get("count", assoc.count)
                assoc.unit_price = product_inst.price
            else:
                assoc = OrderProductAssociation(
                    order_id=obj.id,
                    product_id=upd_product["product_id"],
                    count=upd_product.get("count", 0),
                    unit_price=product_inst.price,
                )
                obj.products_details.append(assoc)

        await session.flush()
        return obj
