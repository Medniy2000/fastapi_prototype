from src.app.infrastructure.repositories.container import container as repo_container
from src.app.application.common.services.base import BaseApplicationService


class AppUserService(BaseApplicationService):
    repository = repo_container.users_repository
