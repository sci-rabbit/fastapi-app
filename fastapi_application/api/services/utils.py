import sqlalchemy.exc
from fastapi import HTTPException


async def handle_integrity_error(
    func, *args, message="Object already exists", **kwargs
):
    try:
        return await func(*args, **kwargs)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=400, detail=message)
