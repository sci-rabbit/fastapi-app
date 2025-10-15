import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from fastapi_application.core.models.category import Category
    from fastapi_application.core.models import OrderProductAssociation


class Product(Base):

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[int]
    description: Mapped[str]
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=True, index=True
    )
    category: Mapped["Category"] = relationship("Category", back_populates="products")

    orders_details: Mapped[list["OrderProductAssociation"]] = relationship(
        back_populates="product"
    )
