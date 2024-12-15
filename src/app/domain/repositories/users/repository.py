from src.app.core.models.users import User
from src.app.domain.entities.users import UserEntity
from src.app.domain.repositories.base import BaseSQLAsyncDrivenBaseRepository


class UsersRepository(BaseSQLAsyncDrivenBaseRepository):
    MODEL = User
    ENTITY = UserEntity
