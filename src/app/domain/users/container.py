# flake8: noqa
from typing import Type
import src
from src.app.domain.common.container import DomainBaseServicesContainer


class DomainUsersServiceContainer(DomainBaseServicesContainer):

    @property
    def users_service(self) -> Type["src.app.domain.users.services.users_service.DomainUsersService"]:
        from src.app.domain.users.services.users_service import DomainUsersService
        return DomainUsersService


container = DomainUsersServiceContainer()
