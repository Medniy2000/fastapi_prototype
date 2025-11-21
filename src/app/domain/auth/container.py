# flake8: noqa
from typing import Type
import src
from src.app.domain.common.container import DomainBaseServicesContainer


class DomainAuthServiceContainer(DomainBaseServicesContainer):

    @property
    def auth_service(self) -> Type["src.app.domain.auth.services.auth_service.DomainAuthService"]:
        from src.app.domain.auth.services.auth_service import DomainAuthService

        return DomainAuthService

    @property
    def jwt_service(self) -> Type["src.app.domain.auth.services.jwt_service.DomainJWTService"]:
        from src.app.domain.auth.services.jwt_service import DomainJWTService

        return DomainJWTService


container = DomainAuthServiceContainer()
