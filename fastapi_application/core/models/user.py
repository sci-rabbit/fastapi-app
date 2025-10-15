from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from fastapi_application.core.models import Post, Order


class User(Base, SQLAlchemyBaseUserTableUUID):

    first_name: Mapped[str | None] = mapped_column(String(44))
    second_name: Mapped[str | None] = mapped_column(String(44))
    username: Mapped[str] = mapped_column(
        String(44),
        nullable=False,
        unique=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(44),
        nullable=False,
        unique=True,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(11), default="user")

    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, first_name={self.first_name}, last_name={self.second_name})>"
