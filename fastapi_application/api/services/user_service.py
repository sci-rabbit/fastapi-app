from uuid import UUID

import structlog
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_application.core.models import User
from fastapi_application.core.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserUpdatePartial,
)
from fastapi_application.api.services.utils import handle_integrity_error, get_or_404
from fastapi_application.api.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

logger = structlog.get_logger()


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
            "Creating user",
            username=user_data.username,
            email=user_data.email,
        )

        try:
            user_dict = user_data.model_dump()

            user = await handle_integrity_error(
                self.user_repo.create,
                session,
                user_dict,
                message="User with that email or username already exists",
            )

            logger.info(
                "User created successfully",
                user_id=str(user.id),
                username=user_data.username,
                email=user_data.email,
            )
            return user

        except Exception as e:
            logger.error(
                "Failed to create user",
                username=user_data.username,
                email=user_data.email,
                error=str(e),
                exc_info=True,
            )
            raise

    async def get_user(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User:
        logger.info("Getting user", user_id=str(user_id))

        user = await self.user_repo.get(session, user_id)
        if not user:
            logger.warning("User not found", user_id=str(user_id))
        get_or_404(user)

        logger.info("User retrieved successfully", user_id=str(user_id))
        return user

    async def get_all_users(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        logger.info("Retrieving all users", limit=limit, offset=offset)

        users = await self.user_repo.get_all(session, limit, offset)

        logger.info(
            "Users retrieved successfully",
            count=len(users),
            limit=limit,
            offset=offset,
        )
        return users

    async def get_many_users(
        self,
        session: AsyncSession,
        user_ids: list[UUID],
    ) -> list[User]:
        logger.info(
            "Retrieving multiple users",
            user_ids=[str(uid) for uid in user_ids],
        )

        users = await self.user_repo.get_many(session, user_ids)

        logger.info(
            "Multiple users retrieved successfully",
            retrieved_count=len(users),
        )
        return users

    async def get_users_with_paginated(
        self,
        session: AsyncSession,
        params: Params | None = None,
    ) -> Page[User]:
        logger.info("Retrieving paginated users")

        page = await self.user_repo.get_multi_paginated(session, params=params)

        logger.info("Paginated users retrieved", total_items=page.total)
        return page

    async def update_user_with_partial(
        self,
        session: AsyncSession,
        user: User,
        user_upd: UserUpdate | UserUpdatePartial,
        partial: bool = False,
    ) -> User:
        logger.info(
            "Updating user",
            user_id=str(user.id),
            partial=partial,
        )

        try:
            user_dict = user_upd.model_dump(exclude_unset=partial)
            updated_user = await self.user_repo.update_partial(session, user, user_dict)

            logger.info(
                "User updated successfully",
                user_id=str(updated_user.id),
                partial=partial,
            )
            return updated_user

        except Exception as e:
            logger.error(
                "Failed to update user",
                user_id=str(user.id),
                error=str(e),
                exc_info=True,
            )
            raise

    async def delete_user(
        self,
        session: AsyncSession,
        user: User,
    ) -> None:
        logger.info("Deleting user", user_id=str(user.id))

        await self.user_repo.delete(session, user)

        logger.info("User deleted successfully", user_id=str(user.id))

    async def get_user_by_username(
        self,
        session: AsyncSession,
        username: str,
    ):
        logger.info("Getting user by username", username=username)

        user = await self.user_repo.get_by_username(session, username)
        if not user:
            logger.warning("User not found by username", username=username)
        get_or_404(user)

        logger.info("User retrieved successfully by username", username=username)
        return user

    async def get_user_by_email(
        self,
        session: AsyncSession,
        email: str,
    ):
        logger.info("Getting user by email", email=email)

        user = await self.user_repo.get_by_email(session, email)
        if not user:
            logger.warning("User not found by email", email=email)
        get_or_404(user)

        logger.info("User retrieved successfully by email", email=email)
        return user

    async def get_users_with_orders(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ):
        logger.info("Retrieving users with orders", limit=limit, offset=offset)

        users = await self.user_repo.get_with_orders(session, limit, offset)

        logger.info(
            "Users with orders retrieved successfully",
            count=len(users),
        )
        return users

    async def get_users_with_posts(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ):
        logger.info("Retrieving users with posts", limit=limit, offset=offset)

        users = await self.user_repo.get_with_posts(session, limit, offset)

        logger.info(
            "Users with posts retrieved successfully",
            count=len(users),
        )
        return users

    async def get_many_users_with_orders(
        self,
        session: AsyncSession,
        user_ids: list[UUID],
    ):
        logger.info(
            "Retrieving many users with orders",
            user_ids=[str(uid) for uid in user_ids],
        )

        users = await self.user_repo.get_many_with_orders(session, user_ids)

        logger.info(
            "Many users with orders retrieved successfully",
            retrieved_count=len(users),
        )
        return users

    async def get_many_users_with_posts(
        self,
        session: AsyncSession,
        user_ids: list[UUID],
    ):
        logger.info(
            "Retrieving many users with posts",
            user_ids=[str(uid) for uid in user_ids],
        )

        users = await self.user_repo.get_many_with_posts(session, user_ids)

        logger.info(
            "Many users with posts retrieved successfully",
            retrieved_count=len(users),
        )
        return users
