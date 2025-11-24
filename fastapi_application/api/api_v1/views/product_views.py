from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter
from fastapi_cache.decorator import cache
from fastapi_pagination import Params

from fastapi_application.core.config import settings
from fastapi_application.core.schemas.product_schema import (
    ProductSchema,
    ProductCreate,
    ProductUpdate,
    ProductUpdatePartial,
)
from fastapi_application.core.services.product_service import ProductService
from fastapi_application.api.api_v1.views.main_dependencies_for_views import db_session
from fastapi_application.api.api_v1.views.utils import run_crud_action

from fastapi_application.core.repositories.category_repository import (
    SQLAlchemyCategoryRepository,
)
from fastapi_application.core.repositories import obj_by_id_factory
from fastapi_application.core.repositories import (
    SQLAlchemyProductRepository,
)


product_dep = Annotated[
    ProductSchema,
    Depends(
        obj_by_id_factory(
            SQLAlchemyProductRepository(),
            param_name="product_id",
        )
    ),
]


product_router = APIRouter(
    prefix=settings.api.v1.products,
    tags=["Products CRUD"],
)


product_service = ProductService(
    product_repo=SQLAlchemyProductRepository(),
    category_repo=SQLAlchemyCategoryRepository(),
)


@product_router.get("/")
async def get_products(
    session: db_session,
    limit: int = 50,
    offset: int = 0,
) -> list[ProductSchema]:
    return await run_crud_action(
        session,
        product_service.get_all_products,
        ProductSchema,
        refresh=False,
        limit=limit,
        offset=offset,
    )


@product_router.get("/{product_id}")
@cache(expire=300)
async def get_product_by_id(
    session: db_session,
    product_id: UUID,
) -> ProductSchema:
    return await run_crud_action(
        session,
        product_service.get_product,
        ProductSchema,
        refresh=False,
        product_id=product_id,
    )


@product_router.post("/many")
async def get_products_by_ids(
    session: db_session,
    product_ids: list[UUID],
) -> list[ProductSchema]:
    return await run_crud_action(
        session,
        product_service.get_many_products,
        ProductSchema,
        refresh=False,
        product_ids=product_ids,
    )


@product_router.get("/paginated")
async def get_orders_with_pagination(
    session: db_session,
    params: Annotated[Params, Depends()],
) -> list[ProductSchema]:
    return await run_crud_action(
        session,
        product_service.get_products_with_paginated,
        ProductSchema,
        refresh=False,
        params=params,
    )


@product_router.post("/")
async def create_product(
    session: db_session,
    product_data: Annotated[ProductCreate, Depends()],
) -> ProductSchema:
    return await run_crud_action(
        session,
        product_service.create_product,
        ProductSchema,
        product_data=product_data,
    )


@product_router.put("/{product_id}")
async def update_product(
    session: db_session,
    product: product_dep,
    product_upd: ProductUpdate,
) -> ProductSchema:
    return await run_crud_action(
        session,
        product_service.update_product_with_partial,
        ProductSchema,
        product=product,
        product_upd=product_upd,
    )


@product_router.patch("/{product_id}")
async def update_product(
    session: db_session,
    product: product_dep,
    product_upd: ProductUpdatePartial,
) -> ProductSchema:
    return await run_crud_action(
        session,
        product_service.update_product_with_partial,
        ProductSchema,
        product=product,
        product_upd=product_upd,
        partial=True,
    )


@product_router.delete("/{product_id}")
async def delete_order(
    session: db_session,
    product: product_dep,
) -> None:
    if not session.in_transaction():
        async with session.begin():
            await product_service.delete_product(session, product)
    else:
        await product_service.delete_product(session, product)
