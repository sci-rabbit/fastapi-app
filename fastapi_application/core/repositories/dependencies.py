from typing import Annotated
from uuid import UUID

from fastapi import Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_application.core.db import get_session
from fastapi_application.core.repositories.base_repository import ModelT, BaseRepository


def obj_by_id_factory(repo: BaseRepository, param_name: str):
    async def _obj_by_id(
        obj_id: Annotated[UUID, Path(..., alias=param_name)],
        session: Annotated[AsyncSession, Depends(get_session)],
    ) -> ModelT:
        obj_instance = await repo.get(session, obj_id)

        if obj_instance:
            return obj_instance
        raise HTTPException(status_code=404, detail="Not found")

    return _obj_by_id
