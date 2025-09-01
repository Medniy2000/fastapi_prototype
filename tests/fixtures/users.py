from asyncio import AbstractEventLoop

import pytest
from loguru import logger
from sqlalchemy import delete, insert, text

from src.app.infrastructure.persistence.models.container import container as models_container
from src.app.extensions.psql_ext.psql_ext import get_session
from tests.fixtures.constants import USERS


@pytest.fixture(scope="function")
def users(e_loop: AbstractEventLoop) -> None:  # type: ignore

    logger.info("Setting up fixtures data for users")

    async def startup() -> None:  # noqa
        async with get_session() as session:
            # Prepare users
            user_model = models_container.user
            for user in USERS:
                stmt = insert(user_model).values(**user)
                await session.execute(stmt)
                await session.commit()

            await session.execute(text("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));"))
            await session.commit()

    e_loop.run_until_complete(startup())

    yield

    logger.debug("Cleaning fixtures for users..")

    async def tear_down() -> None:
        models_to_delete = [models_container.user]
        async with get_session() as session:
            for model in models_to_delete:
                stmt = delete(model)
                await session.execute(stmt)
                await session.commit()
            await session.execute(text("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));"))
            await session.commit()

    e_loop.run_until_complete(tear_down())

    logger.debug("Cleaning fixtures for users finished.")
