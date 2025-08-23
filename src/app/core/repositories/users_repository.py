from src.app.core.models.users import User
from src.app.core.repositories.base import BaseSQLAsyncDrivenBaseRepository
from src.app.domain.users.aggregates.users import UserAggregate


class UsersRepository(BaseSQLAsyncDrivenBaseRepository):
    MODEL = User
    OUT_ENTITY = UserAggregate
