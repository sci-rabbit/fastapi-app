import logging
from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_application.core.models import User
from fastapi_application.core.schemas import UserCreate, UserUpdate, UserUpdatePartial
from fastapi_application.api.services.utils import handle_integrity_error
from fastapi_application.api.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        user_repo: SQLAlchemyUserRepository,
    ) -> None:
        self.user_repo = user_repo

    async def create_user(
        self,
        session: AsyncSession,
        user_data: UserCreate,
    ) -> User:
        logger.info(
            "Create user requested",
            extra={
                "username": user_data.username,
                "email": user_data.email,
            },
        )

        user_dict = user_data.model_dump()

        user = await handle_integrity_error(
            self.user_repo.create,
            session,
            user_dict,
            message="User with that email or username already exists",
        )

        logger.info("User created", extra={"User_id": str(user.id)})
        return user

    async def get_user(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User:
        user = await self.user_repo.get(session, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_all_users(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        return await self.user_repo.get_all(
            session,
            limit,
            offset,
        )

    async def get_many_users(
        self,
        session: AsyncSession,
        user_ids: list[UUID],
    ) -> list[User]:
        return await self.user_repo.get_many(
            session,
            user_ids,
        )

    async def get_users_with_paginated(
        self,
        session: AsyncSession,
        params: Params | None = None,
    ) -> Page[User]:
        return await self.user_repo.get_multi_paginated(
            session,
            params=params,
        )

    async def update_user_with_partial(
        self,
        session: AsyncSession,
        user: User,
        user_upd: UserUpdate | UserUpdatePartial,
        partial: bool = False,
    ) -> User:
        user_dict = user_upd.model_dump(exclude_unset=partial)
        return await self.user_repo.update_partial(
            session,
            user,
            user_dict,
        )

    async def delete_user(
        self,
        session: AsyncSession,
        user: User,
    ) -> None:
        await self.user_repo.delete(session, user)

    async def get_user_by_username(
        self,
        session: AsyncSession,
        username: str,
    ):
        user = await self.user_repo.get_by_username(session, username)
        if user is None:
            raise HTTPException(
                status_code=404, detail="User with that username not found"
            )
        return user

    async def get_user_by_email(
        self,
        session: AsyncSession,
        email: str,
    ):
        user = await self.user_repo.get_by_email(session, email)
        if user is None:
            raise HTTPException(
                status_code=404, detail="User with that email not found"
            )
        return user

    async def get_users_with_orders(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ):
        return await self.user_repo.get_with_orders(
            session,
            limit,
            offset,
        )

    async def get_users_with_posts(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ):
        return await self.user_repo.get_with_posts(
            session,
            limit,
            offset,
        )

    async def get_many_users_with_orders(
        self,
        session: AsyncSession,
        user_ids: list[UUID],
    ):
        return await self.user_repo.get_many_with_orders(
            session,
            user_ids,
        )

    async def get_many_users_with_posts(
        self,
        session: AsyncSession,
        user_ids: list[UUID],
    ):
        return await self.user_repo.get_many_with_posts(
            session,
            user_ids,
        )
