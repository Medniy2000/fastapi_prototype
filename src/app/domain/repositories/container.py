from typing import NamedTuple, Type

from src.app.domain.repositories.users.repository import UsersRepository


class RepositoriesContainer(NamedTuple):
    users_repository: Type[UsersRepository]


container = RepositoriesContainer(users_repository=UsersRepository)
