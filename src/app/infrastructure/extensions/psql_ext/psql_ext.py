from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.app.config.settings import settings


class Base(DeclarativeBase):
    pass

CONNECTIONS_POOL_USE_LIFO: bool = True  # LIFO for better connection reuse
DB_JIT_DISABLED: bool = True  # Disable JIT
DB_ISOLATION_LEVEL: str = "READ COMMITTED"

# Init connection for own database ...
default_engine = create_async_engine(
    settings.DB_URL,
    pool_size=settings.CONNECTIONS_POOL_MIN_SIZE,
    max_overflow=settings.CONNECTIONS_POOL_MAX_OVERFLOW,
    pool_recycle=settings.CONNECTIONS_POOL_RECYCLE,
    pool_timeout=settings.CONNECTIONS_POOL_TIMEOUT,
    pool_use_lifo=CONNECTIONS_POOL_USE_LIFO,
    pool_pre_ping=True,
    future=True,
    echo_pool=True,
    echo=settings.SHOW_SQL,
    isolation_level=DB_ISOLATION_LEVEL,
    connect_args={"server_settings": {"jit": "off" if DB_JIT_DISABLED else "on"}},
)

default_session = async_sessionmaker(
    default_engine,
    class_=AsyncSession,
    expire_on_commit=True,
)


# Allowed isolation levels for validation
ALLOWED_ISOLATION_LEVELS = {
    "READ UNCOMMITTED",
    "READ COMMITTED",
    "REPEATABLE READ",
    "SERIALIZABLE",
}


@asynccontextmanager
async def get_session(
    expire_on_commit: bool = False,
    isolation_level: str | None = None,
) -> AsyncGenerator:

    # Validate isolation level to prevent SQL injection
    if isolation_level and isolation_level not in ALLOWED_ISOLATION_LEVELS:
        raise ValueError(
            f"Invalid isolation level: '{isolation_level}'. "
            f"Allowed values: {', '.join(sorted(ALLOWED_ISOLATION_LEVELS))}"
        )

    try:
        async with default_session(expire_on_commit=expire_on_commit) as session:
            if isolation_level:
                # Safe to use string formatting after validation
                await session.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"))
            yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


sync_engine = create_engine(settings.DB_URL_SYNC)
autocommit_engine = sync_engine.execution_options(isolation_level="AUTOCOMMIT")
autocommit_session = sessionmaker(autocommit_engine)
