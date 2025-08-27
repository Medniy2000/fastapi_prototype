from src.app.core.repositories.container import container as repo_container
from src.app.domain.common.services.base import BaseEntityService


class UserService(BaseEntityService):
    repository = repo_container.users_repository
