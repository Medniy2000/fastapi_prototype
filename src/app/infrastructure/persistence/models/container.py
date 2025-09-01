from typing import List, NamedTuple, Type

from src.app.infrastructure.persistence.models.users import User
from src.app.extensions.psql_ext.psql_ext import Base


class ModelsContainer(NamedTuple):
    all: List[Type[Base]]
    base: Type[Base]
    user: Type[User]


container = ModelsContainer(all=[User], base=Base, user=User)
