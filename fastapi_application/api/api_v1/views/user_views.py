from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter
from fastapi_pagination import Params

from fastapi_application.core.config import settings
from fastapi_application.core.schemas import UserUpdate, UserUpdatePartial
from fastapi_application.core.schemas.user_schema import (
    UserSchema,
    UserCreate,
    UserSchemaWithPosts,
    UserSchemaWithOrders,
)

from fastapi_application.api.services.user_service import UserService
from fastapi_application.api.api_v1.views.main_dependencies_for_views import db_session
from fastapi_application.api.api_v1.views.utils import run_crud_action
from fastapi_application.api.repositories.dependencies import obj_by_id_factory
from fastapi_application.api.repositories.user_repository import (
    SQLAlchemyUserRepository,
)


user_dep = Annotated[
    UserSchema,
    Depends(obj_by_id_factory(SQLAlchemyUserRepository(), param_name="user_id")),
]


user_router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["User CRUD"],
)


user_service = UserService(
    user_repo=SQLAlchemyUserRepository(),
)


@user_router.get("/")
async def get_users(
    session: db_session,
    limit: int = 50,
    offset: int = 0,
) -> list[UserSchema]:
    return await run_crud_action(
        session,
        user_service.get_all_users,
        UserSchema,
        refresh=False,
        limit=limit,
        offset=offset,
    )


@user_router.get("/{user_id}")
async def get_user_by_id(
    session: db_session,
    user_id: UUID,
) -> UserSchema:
    return await run_crud_action(
        session,
        user_service.get_user,
        UserSchema,
        refresh=False,
        user_id=user_id,
    )


@user_router.post("/many")
async def get_users_by_ids(
    session: db_session,
    user_ids: list[UUID],
) -> list[UserSchema]:
    return await run_crud_action(
        session,
        user_service.get_many_users,
        UserSchema,
        refresh=False,
        user_ids=user_ids,
    )


@user_router.get("/user/{username}")
async def get_user_by_username(
    session: db_session,
    username: str,
) -> UserSchema:
    return await run_crud_action(
        session,
        user_service.get_user_by_username,
        UserSchema,
        refresh=False,
        username=username,
    )


@user_router.get("/user/mail/{email}")
async def get_user_by_email(
    session: db_session,
    email: str,
) -> UserSchema:
    return await run_crud_action(
        session,
        user_service.get_user_by_email,
        UserSchema,
        refresh=False,
        email=email,
    )


@user_router.post("/many/with_orders")
async def get_many_users_with_orders(
    session: db_session,
    user_ids: list[UUID],
) -> list[UserSchemaWithOrders]:
    return await run_crud_action(
        session,
        user_service.get_many_users_with_orders,
        UserSchemaWithOrders,
        refresh=False,
        user_ids=user_ids,
    )


@user_router.post("/many/with_posts")
async def get_many_users_with_posts(
    session: db_session,
    user_ids: list[UUID],
) -> list[UserSchemaWithPosts]:
    return await run_crud_action(
        session,
        user_service.get_many_users_with_posts,
        UserSchemaWithPosts,
        refresh=False,
        user_ids=user_ids,
    )


@user_router.post("/with_orders")
async def get_users_with_orders(
    session: db_session,
    limit: int = 50,
    offset: int = 0,
) -> list[UserSchemaWithOrders]:
    return await run_crud_action(
        session,
        user_service.get_users_with_orders,
        UserSchemaWithOrders,
        refresh=False,
        limit=limit,
        offset=offset,
    )


@user_router.post("/with_posts")
async def get_users_with_posts(
    session: db_session,
    limit: int = 50,
    offset: int = 0,
) -> list[UserSchemaWithPosts]:
    return await run_crud_action(
        session,
        user_service.get_users_with_posts,
        UserSchemaWithPosts,
        refresh=False,
        limit=limit,
        offset=offset,
    )


@user_router.post("/paginated")
async def get_users_with_pagination(
    session: db_session,
    params: Annotated[Params, Depends()],
) -> list[UserSchema]:
    return await run_crud_action(
        session,
        user_service.get_users_with_paginated,
        UserSchema,
        refresh=False,
        params=params,
    )


@user_router.post("/")
async def create_user(
    session: db_session,
    user_data: Annotated[UserCreate, Depends()],
) -> UserSchema:
    return await run_crud_action(
        session,
        user_service.create_user,
        UserSchema,
        user_data=user_data,
    )


@user_router.put("/{user_id}")
async def update_user(
    session: db_session,
    user: user_dep,
    user_upd: UserUpdate,
) -> UserSchema:
    return await run_crud_action(
        session,
        user_service.update_user_with_partial,
        UserSchema,
        user=user,
        user_upd=user_upd,
    )


@user_router.patch("/{user_id}")
async def update_user_partial(
    session: db_session,
    user: user_dep,
    user_upd: UserUpdatePartial,
) -> UserSchema:
    return await run_crud_action(
        session,
        user_service.update_user_with_partial,
        UserSchema,
        user=user,
        user_upd=user_upd,
        partial=True,
    )


@user_router.delete("/{user_id}")
async def delete_user(
    session: db_session,
    user: user_dep,
) -> None:
    async with session.begin():
        await user_service.delete_user(session, user)
