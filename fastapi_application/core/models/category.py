from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from fastapi_application.core.models.product import Product


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="category"
    )
