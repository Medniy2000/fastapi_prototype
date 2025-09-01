# flake8: noqa
from typing import Type


class DomainServicesContainer:

    @property
    def auth_service(self) -> Type["src.app.domain.users.services.auth_service.AuthDomainService"]:  # noqa
        from src.app.domain.users.services.auth_service import AuthDomainService

        return AuthDomainService


container = DomainServicesContainer()
