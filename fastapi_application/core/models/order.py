from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from . import UserRelationMixin
from .base import Base

if TYPE_CHECKING:
    from fastapi_application.core.models.order_product_association import (
        OrderProductAssociation,
    )


class Order(UserRelationMixin, Base):
    _user_id_nullable = True
    _user_id_unique = False
    _user_back_populates = "orders"

    promo_code: Mapped[str | None]

    products_details: Mapped[list["OrderProductAssociation"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
