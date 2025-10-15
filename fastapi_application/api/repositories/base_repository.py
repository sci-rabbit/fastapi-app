import logging
from typing import TypeVar, Protocol
from uuid import UUID

from fastapi_pagination import Params, Page
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


ModelT = TypeVar("ModelT")
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class BaseRepository(Protocol[ModelT]):
    async def get(self, session: AsyncSession, obj_id: UUID) -> ModelT | None: ...
    async def get_all(
        self, session: AsyncSession, limit: int = 50, offset: int = 0
    ) -> list[ModelT]: ...
    async def get_many(
        self, session: AsyncSession, obj_ids: list[UUID | int]
    ) -> list[ModelT]: ...
    async def get_multi_paginated(
        self,
        session: AsyncSession,
        params: Params,
    ) -> Page[ModelT]: ...
    async def create(self, session: AsyncSession, obj_data: dict) -> ModelT: ...
    async def update_partial(
        self, session: AsyncSession, obj: ModelT, obj_upd: dict
    ) -> ModelT: ...
    async def delete(self, session: AsyncSession, obj: ModelT) -> None: ...
