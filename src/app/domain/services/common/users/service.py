from src.app.domain.repositories.container import container as repo_container
from src.app.domain.services.base import BaseEntityService


class UserService(BaseEntityService):
    repository = repo_container.users_repository
