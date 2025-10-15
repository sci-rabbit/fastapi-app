import uuid

from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyBaseAccessTokenTableUUID,
)
from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from fastapi_application.core.models import Base


class AccessToken(Base, SQLAlchemyBaseAccessTokenTableUUID):
    __tablename__ = "access_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="cascade"),
        nullable=False,
    )
