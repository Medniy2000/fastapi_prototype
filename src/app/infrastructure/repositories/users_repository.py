from src.app.infrastructure.persistence.models.container import container as models_container
from src.app.infrastructure.repositories.base.abstract import BasePSQLRepository


class UsersPSQLRepository(BasePSQLRepository):
    MODEL = models_container.user
