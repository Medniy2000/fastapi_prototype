# flake8: noqa
from typing import Type

import src


class ServicesContainer:
    @property
    def users_service(self) -> Type["src.app.domain.services.common.users.service.UserService"]:
        from src.app.domain.services.common.users.service import UserService

        return UserService

    @property
    def auth_service(self) -> Type["src.app.domain.services.auth.auth.service.AuthService"]:
        from src.app.domain.services.auth.auth.service import AuthService

        return AuthService

    @property
    def jwt_service(self) -> Type["src.app.domain.services.auth.jwt.service.JWTService"]:
        from src.app.domain.services.auth.jwt.service import JWTService

        return JWTService


container = ServicesContainer()
