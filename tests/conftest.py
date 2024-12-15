import asyncio
from asyncio import AbstractEventLoop
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app.main import app


@pytest.fixture(scope="session")
def e_loop() -> AbstractEventLoop:
    return asyncio.get_event_loop()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator:
    with TestClient(app) as c:
        yield c


pytest_plugins: list = ["tests.fixtures.users"]
