# flake8: noqa
from typing import Type
import src
from src.app.domain.common.container import DomainBaseServicesContainer


class DomainUsersServiceContainer(DomainBaseServicesContainer):
    pass


container = DomainUsersServiceContainer()
