import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastapi_application.core.models import Base

if TYPE_CHECKING:
    from fastapi_application.core.models.order import Order
    from fastapi_application.core.models.product import Product


class OrderProductAssociation(Base):
    __tablename__ = "order_product_association"
    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "product_id",
            name="idx_unique_order_product",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), index=True)
    count: Mapped[int] = mapped_column(default=1, server_default="1")
    unit_price: Mapped[int] = mapped_column(default=0, server_default="0")

    order: Mapped["Order"] = relationship(back_populates="products_details")
    product: Mapped["Product"] = relationship(back_populates="orders_details")
