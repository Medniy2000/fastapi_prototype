# flake8: noqa
from typing import Type

import src


class ServicesContainer:
    @property
    def users_service(self) -> Type["src.app.domain.users.services.users_service.UserService"]:
        from src.app.domain.users.services.users_service import UserService

        return UserService

    @property
    def auth_service(self) -> Type["src.app.domain.users.services.auth_service.AuthService"]:
        from src.app.domain.users.services.auth_service import AuthService

        return AuthService


container = ServicesContainer()
