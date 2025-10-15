import uuid

from pydantic import BaseModel, ConfigDict

from fastapi_application.core.schemas.product_schema import ProductSchema


class OrderProductAssociationSchema(BaseModel):
    count: int
    unit_price: int
    product: ProductSchema

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    user_id: uuid.UUID | None
    promo_code: str | None = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    pass


class OrderUpdatePartial(OrderBase):
    user_id: uuid.UUID | None = None
    promo_code: str | None = None


class OrderProductIn(BaseModel):
    product_id: uuid.UUID
    count: int

    model_config = ConfigDict(from_attributes=True)


class OrderCreateWithProducts(OrderBase):
    products: list[OrderProductIn]


class OrderProductUpd(BaseModel):
    product_id: uuid.UUID
    count: int


class OrderProductPatch(BaseModel):
    product_id: uuid.UUID
    count: int | None = None


class OrderUpdateWithProducts(OrderBase):
    products_data: list[OrderProductUpd]


class OrderUpdateWithProductsPartial(OrderBase):
    promo_code: str | None = None
    products_data: list[OrderProductPatch] | None = None


class OrderSchema(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class OrderSchemaWithProducts(OrderSchema):
    products_details: list[OrderProductAssociationSchema]
