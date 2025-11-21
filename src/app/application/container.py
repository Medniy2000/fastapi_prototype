# flake8: noqa
from typing import Type

import src


class ApplicationServicesContainer:
    @property
    def users_service(self) -> Type["src.app.application.services.users_service.AppUserService"]:
        from src.app.application.services.users_service import AppUserService

        return AppUserService

    @property
    def auth_service(self) -> Type["src.app.application.services.auth_service.AppUserService"]:
        from src.app.application.services.auth_service import AppUserService

        return AppUserService

    @property
    def common_service(self) -> Type["src.app.application.services.common_service.AppCommonService"]:
        from src.app.application.services.common_service import AppCommonService

        return AppCommonService


container = ApplicationServicesContainer()
