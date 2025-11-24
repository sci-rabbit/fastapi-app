from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter
from fastapi_cache.decorator import cache
from fastapi_pagination import Params

from fastapi_application.core.config import settings
from fastapi_application.core.schemas.category_schema import (
    CategorySchema,
    CategoryCreate,
    CategoryUpdate,
    CategoryUpdatePartial,
    CategoryWithProductsSchema,
)
from fastapi_application.core.services.category_service import CategoryService
from fastapi_application.api.api_v1.views.main_dependencies_for_views import db_session
from fastapi_application.api.api_v1.views.utils import run_crud_action
from fastapi_application.core.repositories.category_repository import (
    SQLAlchemyCategoryRepository,
)
from fastapi_application.core.repositories import obj_by_id_factory


category_dep = Annotated[
    CategorySchema,
    Depends(
        obj_by_id_factory(
            SQLAlchemyCategoryRepository(),
            param_name="category_id",
        )
    ),
]

category_service = CategoryService(category_repo=SQLAlchemyCategoryRepository())

category_router = APIRouter(prefix=settings.api.v1.categories, tags=["Categories CRUD"])


@category_router.get("/")
async def get_categories(
    session: db_session,
    limit: int = 50,
    offset: int = 0,
) -> list[CategorySchema]:
    return await run_crud_action(
        session,
        category_service.get_many_categories,
        CategorySchema,
        refresh=False,
        limit=limit,
        offset=offset,
    )


@category_router.get("/{category_id}")
@cache(expire=300)
async def get_category_by_id(
    session: db_session,
    category_id: UUID,
) -> CategorySchema:
    return await run_crud_action(
        session,
        category_service.get_category,
        CategorySchema,
        refresh=False,
        category_id=category_id,
    )


@category_router.post("/many")
async def get_categories_by_ids(
    session: db_session,
    category_ids: list[UUID],
) -> list[CategorySchema]:
    return await run_crud_action(
        session,
        category_service.get_many_categories,
        CategorySchema,
        refresh=False,
        category_ids=category_ids,
    )


@category_router.post("/paginated")
async def get_categories_with_pagination(
    session: db_session,
    params: Annotated[Params, Depends()],
) -> list[CategorySchema]:
    return await run_crud_action(
        session,
        category_service.get_categories_with_paginated,
        CategorySchema,
        refresh=False,
        params=params,
    )


@category_router.get("/category_with_products/{category_id}")
@cache(expire=300)
async def get_category_with_products(
    session: db_session,
    category_id: UUID,
) -> CategoryWithProductsSchema:
    return await run_crud_action(
        session,
        category_service.get_category_with_products,
        CategoryWithProductsSchema,
        refresh=False,
        category_id=category_id,
    )


@category_router.post("/")
async def create_category(
    session: db_session,
    category_data: Annotated[CategoryCreate, Depends()],
) -> CategorySchema:
    return await run_crud_action(
        session,
        category_service.create_category,
        CategorySchema,
        category_data=category_data,
    )


@category_router.put("/{category_id}")
async def update_category(
    session: db_session,
    category: category_dep,
    category_upd: CategoryUpdate,
) -> CategorySchema:
    return await run_crud_action(
        session,
        category_service.update_category_with_partial,
        CategorySchema,
        category=category,
        category_upd=category_upd,
    )


@category_router.patch("/{category_id}")
async def update_category_partial(
    session: db_session,
    category: category_dep,
    category_upd: CategoryUpdatePartial,
) -> CategorySchema:
    return await run_crud_action(
        session,
        category_service.update_category_with_partial,
        CategorySchema,
        category=category,
        category_upd=category_upd,
        partial=True,
    )


@category_router.delete("/{category_id}")
async def delete_category(
    session: db_session,
    category: category_dep,
) -> None:
    if not session.in_transaction():
        async with session.begin():
            await category_service.delete_category(
                session,
                category,
            )
    else:
        await category_service.delete_category(
            session,
            category,
        )
