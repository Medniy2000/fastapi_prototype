from typing import NamedTuple, Type

from src.app.infrastructure.repositories.common_psql_repository import CommonPSQLRepository
from src.app.infrastructure.repositories.common_redis_repository import CommonRedisRepository
from src.app.infrastructure.repositories.users_repository import UsersPSQLRepository


class RepositoriesContainer(NamedTuple):

    common_psql_repository: Type[CommonPSQLRepository]
    common_redis_repository: Type[CommonRedisRepository]
    users_repository: Type[UsersPSQLRepository]


container = RepositoriesContainer(
    common_psql_repository=CommonPSQLRepository,
    common_redis_repository=CommonRedisRepository,
    users_repository=UsersPSQLRepository,
)
