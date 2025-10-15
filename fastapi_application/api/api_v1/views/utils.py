from typing import Callable, Awaitable, Any, Type

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


async def run_crud_action(
    session: AsyncSession,
    func: Callable[..., Awaitable[Any]],
    schema: Type[BaseModel] | None = None,
    refresh: bool = True,
    *args,
    **kwargs,
) -> Any:
    if not session.in_transaction():
        async with session.begin():
            result = await func(session, *args, **kwargs)
    else:
        result = await func(session, *args, **kwargs)

    if refresh and not isinstance(result, list):
        await session.refresh(result)

    if schema:
        if isinstance(result, list):
            return [schema.model_validate(obj) for obj in result]
        return schema.model_validate(result)
    return result
