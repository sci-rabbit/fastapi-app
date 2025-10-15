import uuid
from datetime import datetime
from uuid import uuid4

from sqlalchemy import func, UUID, TIMESTAMP
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    mapped_column,
    Mapped,
)


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls):
        return f"{cls.__name__.lower()}s"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )
