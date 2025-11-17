import sqlalchemy.exc
from fastapi import HTTPException

from fastapi_application.api.repositories.base_repository import ModelT


async def handle_integrity_error(
    func, *args, message="Object already exists", **kwargs
):
    try:
        return await func(*args, **kwargs)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=400, detail=message)


def get_or_404(
    obj: ModelT,
) -> None:
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{obj.__name__} not found")
