import uuid
from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    price: int
    description: str


class ProductCreate(ProductBase):
    category_name: str | None = None


class ProductUpdate(ProductBase):
    category_name: str | None


class ProductUpdatePartial(ProductBase):
    name: str | None = None
    price: int | None = None
    description: str | None = None
    category_name: str | None = None


class ProductSchema(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID | None
