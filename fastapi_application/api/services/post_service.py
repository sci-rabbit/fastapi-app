import logging
from uuid import UUID

from fastapi import HTTPException
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_application.core.models import Post
from fastapi_application.core.schemas.post_schema import (
    PostCreate,
    PostUpdate,
    PostUpdatePartial,
)
from fastapi_application.api.repositories.post_repository import (
    SQLAlchemyPostRepository,
)


logger = logging.getLogger(__name__)


class PostService:
    def __init__(
        self,
        post_repo: SQLAlchemyPostRepository,
    ) -> None:
        self.post_repo = post_repo

    async def create_post(
        self,
        session: AsyncSession,
        post_data: PostCreate,
    ) -> Post:
        logger.info(
            "Create post requested",
            extra={
                "User": (str(post_data.user_id)),
                "Post Title": (str(post_data.tittle)),
                "Post Body": (str(post_data.body)),
            },
        )

        post_dict = post_data.model_dump()
        post = await self.post_repo.create(
            session,
            post_dict,
        )
        logger.info("Post created", extra={"post_id": str(post.id)})
        return post

    async def get_post(
        self,
        session: AsyncSession,
        post_id: UUID,
    ) -> Post:
        post = await self.post_repo.get(session, post_id)
        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    async def get_all_posts(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Post]:
        return await self.post_repo.get_all(
            session,
            limit,
            offset,
        )

    async def get_many_posts(
        self,
        session: AsyncSession,
        post_ids: list[UUID],
    ) -> list[Post]:
        return await self.post_repo.get_many(
            session,
            post_ids,
        )

    async def get_posts_with_paginated(
        self,
        session: AsyncSession,
        params: Params | None = None,
    ) -> Page[Post]:
        return await self.post_repo.get_multi_paginated(
            session,
            params=params,
        )

    async def update_post_with_partial(
        self,
        session: AsyncSession,
        post: Post,
        post_upd: PostUpdate | PostUpdatePartial,
        partial: bool = False,
    ) -> Post:
        post_dict = post_upd.model_dump(exclude_unset=partial)
        return await self.post_repo.update_partial(
            session,
            post,
            post_dict,
        )

    async def delete_post(
        self,
        session: AsyncSession,
        post: Post,
    ) -> None:
        await self.post_repo.delete(
            session,
            post,
        )
