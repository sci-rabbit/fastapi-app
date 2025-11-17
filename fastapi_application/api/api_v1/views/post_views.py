from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter
from fastapi_cache.decorator import cache
from fastapi_pagination import Params

from fastapi_application.core.config import settings
from fastapi_application.core.schemas.post_schema import (
    PostSchema,
    PostCreate,
    PostUpdate,
    PostUpdatePartial,
)

from fastapi_application.api.services.post_service import PostService
from fastapi_application.api.api_v1.views.main_dependencies_for_views import db_session
from fastapi_application.api.api_v1.views.utils import run_crud_action

from fastapi_application.api.repositories.dependencies import obj_by_id_factory
from fastapi_application.api.repositories.post_repository import (
    SQLAlchemyPostRepository,
)

post_dep = Annotated[
    PostSchema,
    Depends(obj_by_id_factory(SQLAlchemyPostRepository(), param_name="post_id")),
]


post_router = APIRouter(prefix=settings.api.v1.posts, tags=["Posts CRUD"])

post_service = PostService(post_repo=SQLAlchemyPostRepository())


@post_router.get("/")
async def get_posts(
    session: db_session,
    limit: int = 50,
    offset: int = 0,
) -> list[PostSchema]:
    return await run_crud_action(
        session,
        post_service.get_all_posts,
        PostSchema,
        refresh=False,
        limit=limit,
        offset=offset,
    )


@post_router.get("/{post_id}")
@cache(expire=300)
async def get_post_by_id(
    session: db_session,
    post_id: UUID,
) -> PostSchema:
    return await run_crud_action(
        session,
        post_service.get_post,
        PostSchema,
        refresh=False,
        post_id=post_id,
    )


@post_router.post("/many")
async def get_posts_by_ids(
    session: db_session,
    post_ids: list[UUID],
) -> list[PostSchema]:
    return await run_crud_action(
        session,
        post_service.get_many_posts,
        PostSchema,
        refresh=False,
        post_ids=post_ids,
    )


@post_router.get("/paginated")
async def get_posts_with_pagination(
    session: db_session,
    params: Annotated[Params, Depends()],
) -> list[PostSchema]:
    return await run_crud_action(
        session,
        post_service.get_posts_with_paginated,
        PostSchema,
        refresh=False,
        params=params,
    )


@post_router.post("/")
async def create_post(
    session: db_session,
    post_data: Annotated[PostCreate, Depends()],
) -> PostSchema:
    return await run_crud_action(
        session,
        post_service.create_post,
        PostSchema,
        post_data=post_data,
    )


@post_router.put("/{post_id}")
async def update_post(
    session: db_session,
    post: post_dep,
    post_upd: PostUpdate,
) -> PostSchema:
    return await run_crud_action(
        session,
        post_service.update_post_with_partial,
        PostSchema,
        post=post,
        post_upd=post_upd,
    )


@post_router.patch("/{post_id}")
async def update_post_partial(
    session: db_session,
    post: post_dep,
    post_upd: PostUpdatePartial,
) -> PostSchema:
    return await run_crud_action(
        session,
        post_service.update_post_with_partial,
        PostSchema,
        post=post,
        post_upd=post_upd,
        partial=True,
    )


@post_router.delete("/{post_id}")
async def delete_post(
    session: db_session,
    post: post_dep,
) -> None:
    async with session.begin():
        await post_service.delete_post(
            session,
            post,
        )
