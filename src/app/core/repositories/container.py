from typing import NamedTuple, Type

from src.app.core.repositories.users_repository import UsersRepository


class RepositoriesContainer(NamedTuple):
    users_repository: Type[UsersRepository]


container = RepositoriesContainer(users_repository=UsersRepository)
