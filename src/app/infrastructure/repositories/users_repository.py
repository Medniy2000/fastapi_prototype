from src.app.infrastructure.persistence.models.container import container as models_container
from src.app.infrastructure.repositories.base import BaseSQLAsyncDrivenBaseRepository


class UsersRepository(BaseSQLAsyncDrivenBaseRepository):
    MODEL = models_container.user
