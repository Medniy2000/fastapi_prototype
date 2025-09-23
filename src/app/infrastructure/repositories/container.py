from typing import NamedTuple, Type

from src.app.infrastructure.repositories.users_repository import UsersPSQLRepository


class RepositoriesContainer(NamedTuple):
    users_repository: Type[UsersPSQLRepository]


container = RepositoriesContainer(users_repository=UsersPSQLRepository)
