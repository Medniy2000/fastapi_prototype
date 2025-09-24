# flake8: noqa
from typing import Type

import src


class ApplicationServicesContainer:
    @property
    def users_service(self) -> Type["src.app.application.services.users_service.UserService"]:
        from src.app.application.services.users_service import UserService

        return UserService

    @property
    def auth_service(self) -> Type["src.app.application.services.auth_service.AuthService"]:
        from src.app.application.services.auth_service import AuthService

        return AuthService

    @property
    def common_service(self) -> Type["src.app.application.services.common_service.CommonApplicationService"]:
        from src.app.application.services.common_service import CommonApplicationService

        return CommonApplicationService


container = ApplicationServicesContainer()
