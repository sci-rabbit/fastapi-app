import logging
from uuid import UUID

from fastapi_pagination import Params, Page
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.orm import selectinload

from fastapi_application.core.models import User, Order, OrderProductAssociation
from fastapi_application.api.repositories.base_repository import BaseRepository
from fastapi_application.api.repositories.utils import (
    get_all_handler,
    get_handler,
    get_many_handler,
    get_multi_paginated_handler,
    update_partial_handler,
    delete_handler,
    create_handler,
)

logger = logging.getLogger(__name__)


class SQLAlchemyUserRepository(BaseRepository[User]):

    async def get(
        self,
        session: AsyncSession,
        obj_id: UUID,
    ) -> User | None:
        return await get_handler(
            User,
            session,
            obj_id,
        )

    async def get_all(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        return await get_all_handler(
            User,
            session,
            limit,
            offset,
        )

    async def get_many(
        self,
        session: AsyncSession,
        obj_ids: list[UUID],
    ) -> list[User]:
        return await get_many_handler(
            User,
            session,
            obj_ids,
        )

    async def get_multi_paginated(
        self,
        session: AsyncSession,
        params: Params,
    ) -> Page[User]:
        return await get_multi_paginated_handler(
            User,
            session,
            params,
        )

    async def create(
        self,
        session: AsyncSession,
        obj_data: dict,
    ) -> User:
        return await create_handler(
            User,
            session,
            obj_data,
        )

    async def update_partial(
        self,
        session: AsyncSession,
        obj: User,
        obj_upd: dict,
    ) -> User:
        return await update_partial_handler(
            session,
            obj,
            obj_upd,
        )

    async def delete(
        self,
        session: AsyncSession,
        obj: User,
    ) -> None:
        await delete_handler(
            session,
            obj,
        )

    async def get_by_username(
        self,
        session: AsyncSession,
        username: str,
    ) -> User | None:
        query = select(User).where(User.username == username)
        result: Result = await session.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:
        query = select(User).where(User.email == email)
        result: Result = await session.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_with_posts(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        query = (
            select(User)
            .options(selectinload(User.posts))
            .where(User.posts.any())
            .limit(limit)
            .offset(offset)
        )
        users = await session.scalars(query)

        return list(users)

    async def get_with_orders(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        query = (
            select(User)
            .options(
                selectinload(User.orders)
                .selectinload(Order.products_details)
                .selectinload(OrderProductAssociation.product)
            )
            .where(User.orders.any())
            .limit(limit)
            .offset(offset)
        )
        users = await session.scalars(query)

        return list(users)

    async def get_many_with_posts(
        self,
        session: AsyncSession,
        obj_ids: list[UUID],
    ) -> list[User]:
        if not obj_ids:
            return []

        query = (
            select(User)
            .options(selectinload(User.posts))
            .where(User.posts.any())
            .where(User.id.in_(obj_ids))
        )
        users = await session.scalars(query)

        return list(users)

    async def get_many_with_orders(
        self,
        session: AsyncSession,
        obj_ids: list[UUID],
    ) -> list[User]:
        if not obj_ids:
            return []

        query = (
            select(User)
            .options(
                selectinload(User.orders)
                .selectinload(Order.products_details)
                .selectinload(OrderProductAssociation.product)
            )
            .where(User.orders.any())
            .where(User.id.in_(obj_ids))
        )
        users = await session.scalars(query)

        return list(users)
