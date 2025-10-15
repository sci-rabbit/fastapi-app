import uuid

from pydantic import BaseModel, ConfigDict

from fastapi_application.core.schemas.product_schema import ProductSchema


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryUpdatePartial(CategoryBase):
    name: str | None = None


class CategorySchema(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class CategoryWithProductsSchema(CategorySchema):
    products: list[ProductSchema]
