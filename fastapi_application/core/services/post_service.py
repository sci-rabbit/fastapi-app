import structlog
from uuid import UUID

from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_application.core.services.utils import get_or_404
from fastapi_application.core.models import Post
from fastapi_application.core.schemas.post_schema import (
    PostCreate,
    PostUpdate,
    PostUpdatePartial,
)
from fastapi_application.core.repositories import (
    SQLAlchemyPostRepository,
)

logger = structlog.get_logger()


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
            "Creating post",
            user_id=str(post_data.user_id),
            title=post_data.tittle,
        )

        try:
            post_dict = post_data.model_dump()
            post = await self.post_repo.create(session, post_dict)

            logger.info(
                "Post created successfully",
                post_id=str(post.id),
                user_id=str(post_data.user_id),
                title=post_data.tittle,
            )
            return post

        except Exception as e:
            logger.error(
                "Failed to create post",
                user_id=str(post_data.user_id),
                title=post_data.tittle,
                error=str(e),
                exc_info=True,
            )
            raise

    async def get_post(
        self,
        session: AsyncSession,
        post_id: UUID,
    ) -> Post:
        logger.info("Getting post", post_id=str(post_id))

        post = await self.post_repo.get(session, post_id)
        if not post:
            logger.warning("Post not found", post_id=str(post_id))
        get_or_404(post)

        logger.info("Post retrieved successfully", post_id=str(post_id))
        return post

    async def get_all_posts(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Post]:
        logger.info("Retrieving all posts", limit=limit, offset=offset)

        posts = await self.post_repo.get_all(session, limit, offset)

        logger.info(
            "Posts retrieved successfully",
            count=len(posts),
            limit=limit,
            offset=offset,
        )
        return posts

    async def get_many_posts(
        self,
        session: AsyncSession,
        post_ids: list[UUID],
    ) -> list[Post]:
        logger.info(
            "Retrieving multiple posts",
            post_ids=[str(pid) for pid in post_ids],
        )

        posts = await self.post_repo.get_many(session, post_ids)

        logger.info(
            "Multiple posts retrieved successfully",
            retrieved_count=len(posts),
        )
        return posts

    async def get_posts_with_paginated(
        self,
        session: AsyncSession,
        params: Params | None = None,
    ) -> Page[Post]:
        logger.info("Retrieving paginated posts")
        page = await self.post_repo.get_multi_paginated(session, params=params)
        logger.info("Paginated posts retrieved", total_items=page.total)
        return page

    async def update_post_with_partial(
        self,
        session: AsyncSession,
        post: Post,
        post_upd: PostUpdate | PostUpdatePartial,
        partial: bool = False,
    ) -> Post:
        logger.info(
            "Updating post",
            post_id=str(post.id),
            partial=partial,
        )

        post_dict = post_upd.model_dump(exclude_unset=partial)
        updated_post = await self.post_repo.update_partial(session, post, post_dict)

        logger.info(
            "Post updated successfully",
            post_id=str(updated_post.id),
            partial=partial,
        )
        return updated_post

    async def delete_post(
        self,
        session: AsyncSession,
        post: Post,
    ) -> None:
        logger.info("Deleting post", post_id=str(post.id))

        await self.post_repo.delete(session, post)

        logger.info("Post deleted successfully", post_id=str(post.id))
