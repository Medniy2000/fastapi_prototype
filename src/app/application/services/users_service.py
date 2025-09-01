from src.app.core.repositories.container import container as repo_container
from src.app.application.common.services.base import BaseApplicationService


class UserService(BaseApplicationService):
    repository = repo_container.users_repository
