from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.app.config.settings import settings

Base = declarative_base()

# Init connection for own database ...
default_engine = create_async_engine(
    settings.DB_URL,
    pool_size=settings.CONNECTIONS_POOL_MIN_SIZE,
    max_overflow=settings.CONNECTIONS_POOL_MAX_OVERFLOW,
    pool_recycle=60 * 60 * 3,  # recycle after  3 hours
    pool_pre_ping=True,
    future=True,
    echo_pool=True,
    echo=settings.SHOW_SQL,
    connect_args={"server_settings": {"jit": "off"}},
)

default_session = sessionmaker(
    default_engine,  # type: ignore
    class_=AsyncSession,  # type: ignore
)


@asynccontextmanager
async def get_session(expire_on_commit: bool = False) -> AsyncGenerator:
    try:
        async with default_session(expire_on_commit=expire_on_commit) as session:
            yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


sync_engine = create_engine(settings.DB_URL_SYNC)
autocommit_engine = sync_engine.execution_options(isolation_level="AUTOCOMMIT")
autocommit_session = sessionmaker(autocommit_engine)
