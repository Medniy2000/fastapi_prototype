from typing import NamedTuple, Type

from src.app.infrastructure.repositories.users_repository import UsersRepository


class RepositoriesContainer(NamedTuple):
    users_repository: Type[UsersRepository]


container = RepositoriesContainer(users_repository=UsersRepository)
