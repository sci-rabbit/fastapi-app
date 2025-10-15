from typing import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from fastapi_application.core.config import settings


engine = create_async_engine(
    url=settings.db.url,
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)


async def dispose() -> None:
    await engine.dispose()


async_session = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session
