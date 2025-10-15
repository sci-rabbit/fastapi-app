from fastapi_users import schemas
from pydantic import Field


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    second_name: str
    username: str

    is_active: bool = Field(default=True, exclude=True)
    is_superuser: bool = Field(default=False, exclude=True)
    is_verified: bool = Field(default=False, exclude=True)