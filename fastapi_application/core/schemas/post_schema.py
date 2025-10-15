import uuid
from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    user_id: uuid.UUID
    tittle: Annotated[str, MinLen(3), MaxLen(100)]
    body: Annotated[str, MinLen(20), MaxLen(1000)]


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class PostUpdatePartial(PostBase):
    user_id: uuid.UUID | None = None
    tittle: Annotated[str, MinLen(3), MaxLen(100)] | None = None
    body: Annotated[str, MinLen(20), MaxLen(1000)] | None = None


class PostSchema(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
