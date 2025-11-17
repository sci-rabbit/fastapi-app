from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter
from fastapi_cache.decorator import cache
from fastapi_pagination import Params

from fastapi_application.core.config import settings
from fastapi_application.core.schemas.order_schema import (
    OrderSchema,
    OrderSchemaWithProducts,
    OrderCreate,
    OrderCreateWithProducts,
    OrderUpdate,
    OrderUpdatePartial,
    OrderUpdateWithProductsPartial,
)
from fastapi_application.api.services.order_service import OrderService
from fastapi_application.api.api_v1.views.main_dependencies_for_views import db_session
from fastapi_application.api.api_v1.views.utils import run_crud_action
from fastapi_application.api.repositories.dependencies import obj_by_id_factory
from fastapi_application.api.repositories.order_repository import (
    SQLAlchemyOrderRepository,
)
from fastapi_application.api.repositories.product_repository import (
    SQLAlchemyProductRepository,
)


order_dep = Annotated[
    OrderSchema,
    Depends(obj_by_id_factory(SQLAlchemyOrderRepository(), param_name="order_id")),
]


order_service = OrderService(
    order_repo=SQLAlchemyOrderRepository(),
    product_repo=SQLAlchemyProductRepository(),
)


order_router = APIRouter(prefix=settings.api.v1.orders, tags=["Orders CRUD"])


@order_router.get("/")
async def get_orders(
    session: db_session,
    limit: int = 50,
    offset: int = 0,
    with_assoc: bool = False,
) -> list[OrderSchema] | list[OrderSchemaWithProducts]:
    if with_assoc:
        return await run_crud_action(
            session,
            order_service.get_all_orders,
            OrderSchemaWithProducts,
            refresh=False,
            limit=limit,
            offset=offset,
            with_assoc=with_assoc,
        )

    return await run_crud_action(
        session,
        order_service.get_all_orders,
        OrderSchema,
        refresh=False,
        limit=limit,
        offset=offset,
        with_assoc=with_assoc,
    )


@order_router.get("/{order_id}")
@cache(expire=300)
async def get_order_by_id(
    session: db_session,
    order_id: UUID,
) -> OrderSchema:
    return await run_crud_action(
        session,
        order_service.get_order,
        OrderSchema,
        refresh=False,
        order_id=order_id,
    )


@order_router.post("/many")
async def get_orders_by_ids(
    session: db_session,
    order_ids: list[UUID],
    with_assoc: bool = False,
) -> list[OrderSchema] | list[OrderSchemaWithProducts]:
    if with_assoc:
        return await run_crud_action(
            session,
            order_service.get_many_orders,
            OrderSchemaWithProducts,
            refresh=False,
            order_ids=order_ids,
            with_assoc=with_assoc,
        )

    return await run_crud_action(
        session,
        order_service.get_many_orders,
        OrderSchema,
        refresh=False,
        order_ids=order_ids,
        with_assoc=with_assoc,
    )


@order_router.get("/paginated")
async def get_orders_with_pagination(
    session: db_session,
    params: Annotated[Params, Depends()],
) -> list[OrderSchema]:
    return await run_crud_action(
        session,
        order_service.get_orders_with_paginated,
        OrderSchema,
        refresh=False,
        params=params,
    )


@order_router.post("/")
async def create_order(
    session: db_session,
    order_data: Annotated[OrderCreate, Depends()],
) -> OrderSchema:
    return await run_crud_action(
        session,
        order_service.create_order,
        OrderSchema,
        order_data=order_data,
    )


@order_router.post("/with_products")
async def create_order_with_products(
    session: db_session,
    order_data: OrderCreateWithProducts,
) -> OrderSchemaWithProducts:
    if not session.in_transaction():
        async with session.begin():
            order = await order_service.create_order_with_products(
                session,
                order_data,
            )
    else:
        order = await order_service.create_order_with_products(
            session,
            order_data,
        )

    await session.refresh(order)
    order = await order_service.get_many_orders(
        session,
        [order.id],
        with_assoc=True,
    )
    return OrderSchemaWithProducts.model_validate(order[0])


@order_router.put("/{order_id}")
async def update_order(
    session: db_session,
    order: order_dep,
    order_upd: OrderUpdate,
) -> OrderSchema:
    return await run_crud_action(
        session,
        order_service.update_orders_partial,
        OrderSchema,
        order=order,
        order_upd=order_upd,
    )


@order_router.patch("/{order_id}")
async def update_order_partial(
    session: db_session,
    order: order_dep,
    order_upd: OrderUpdatePartial,
) -> OrderSchema:
    return await run_crud_action(
        session,
        order_service.update_orders_partial,
        OrderSchema,
        order=order,
        order_upd=order_upd,
        partial=True,
    )


@order_router.patch("/with_products/{order_id}")
async def update_order_with_products_partial(
    session: db_session,
    order: order_dep,
    order_upd: OrderUpdateWithProductsPartial,
) -> OrderSchemaWithProducts:
    return await run_crud_action(
        session,
        order_service.update_order_with_products_partial,
        OrderSchemaWithProducts,
        order=order,
        order_upd=order_upd,
        partial=True,
    )


@order_router.delete("/{order_id}")
async def delete_order(
    session: db_session,
    order: order_dep,
) -> None:
    if not session.in_transaction():
        async with session.begin():
            await order_service.delete_order(session, order)
    else:
        await order_service.delete_order(session, order)
