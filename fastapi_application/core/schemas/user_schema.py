import uuid
from datetime import datetime
from typing import Annotated
from uuid import UUID

from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

from fastapi_application.core.schemas.product_schema import ProductSchema


class UserCreateForRegistration(BaseModel):
    first_name: str
    second_name: str
    username: str
    email: EmailStr
    password: str

    @field_validator("username", "email", mode="before")
    def lowercase_fields(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v


class UserBase(BaseModel):
    first_name: Annotated[str, MinLen(3), MaxLen(16)] | None
    second_name: Annotated[str, MinLen(3), MaxLen(16)] | None
    username: Annotated[str, MinLen(3), MaxLen(16)]
    email: EmailStr

    @field_validator("username", "email", mode="before")
    def lowercase_fields(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserUpdatePartial(UserBase):
    first_name: Annotated[str, MinLen(3), MaxLen(16)] | None = None
    second_name: Annotated[str, MinLen(3), MaxLen(16)] | None = None
    username: Annotated[str, MinLen(3), MaxLen(16)] | None = None
    email: EmailStr | None = None
    hashed_password: Annotated[str, MinLen(8), MaxLen(2000)] | None = None


class UserSchema(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    updated_at: datetime
    created_at: datetime
    is_active: bool
    is_superuser: bool
    is_verified: bool


class PostIn(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    tittle: Annotated[str, MinLen(1), MaxLen(100)]
    body: Annotated[str, MinLen(5), MaxLen(1000)]
    model_config = ConfigDict(from_attributes=True)


class UserSchemaWithPosts(UserSchema):
    posts: list[PostIn]
    model_config = ConfigDict(from_attributes=True)


class OrderProductAssociationSchema(BaseModel):
    count: int
    unit_price: int
    product: ProductSchema

    model_config = ConfigDict(from_attributes=True)


class OrderIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    promo_code: str | None = None
    products_details: list[OrderProductAssociationSchema]


class UserSchemaWithOrders(UserSchema):
    orders: list[OrderIn]
