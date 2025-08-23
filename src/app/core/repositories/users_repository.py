from typing import Callable

from src.app.core.models.users import User
from src.app.domain.users.aggregates.users import UserAggregate
from src.app.core.repositories.base import BaseSQLAsyncDrivenBaseRepository


class UsersRepository(BaseSQLAsyncDrivenBaseRepository):
    MODEL = User
    OUT_ENTITY = UserAggregate
