import logging
from typing import TypeVar, Type
from uuid import UUID

from fastapi_pagination import Params, Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


ModelT = TypeVar("ModelT", covariant=True)


async def get_all_handler(
    model: Type[ModelT],
    session: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> list[ModelT]:
    query = select(model).limit(limit).offset(offset)
    res = await session.execute(query)
    return list(res.scalars().all())


async def get_handler(
    model: Type[ModelT],
    session: AsyncSession,
    obj_id: UUID,
) -> ModelT | None:
    return await session.get(model, obj_id)


async def get_many_handler(
    model: Type[ModelT],
    session: AsyncSession,
    obj_ids: list[UUID],
) -> list[ModelT]:
    if not obj_ids:
        return []
    query = select(model).where(model.id.in_(obj_ids))
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_multi_paginated_handler(
    model: Type[ModelT],
    session: AsyncSession,
    params: Params,
) -> Page[ModelT]:
    query = select(model)
    return await paginate(session, query, params, unwrap_mode="auto")


async def create_handler(
    model: Type[ModelT],
    session: AsyncSession,
    obj_data: dict,
) -> ModelT:
    model_instance = model(**obj_data)
    session.add(model_instance)
    await session.flush()
    logger.debug(
        "%s flushed to DB",
        model.__name__,
        extra={"id": str(model_instance.id)},
    )
    return model_instance


async def update_partial_handler(
    session: AsyncSession,
    obj: Type[ModelT],
    obj_upd: dict,
) -> ModelT:
    for name, value in obj_upd.items():
        setattr(obj, name, value)
    await session.flush()
    return obj


async def delete_handler(
    session: AsyncSession,
    obj: Type[ModelT],
) -> None:
    await session.delete(obj)
    await session.flush()
