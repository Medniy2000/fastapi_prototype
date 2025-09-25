from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from src.app.infrastructure.extensions.psql_ext.psql_ext import Base


class RepositoryError(Exception):
    pass

class AbstractRepository(ABC):
    pass


@dataclass
class BaseOutputEntity(ABC):
    pass


BaseModel = TypeVar("BaseModel", bound=Base)
OuterGenericType = TypeVar("OuterGenericType", bound=BaseOutputEntity)


class AbstractBaseRepository(AbstractRepository, Generic[OuterGenericType]):
    MODEL: Optional[Type[Base]] = None

    @classmethod
    async def count(cls, filter_data: dict) -> int:
        raise NotImplementedError

    @classmethod
    async def is_exists(cls, filter_data: dict) -> bool:
        raise NotImplementedError

    @classmethod
    async def get_first(
        cls, filter_data: dict, out_dataclass: Optional[OuterGenericType] = None
    ) -> OuterGenericType | None:
        raise NotImplementedError

    @classmethod
    async def get_list(
        cls, filter_data: dict, order_data: Tuple[str] = ("id",), out_dataclass: Optional[OuterGenericType] = None
    ) -> List[OuterGenericType]:
        raise NotImplementedError

    @classmethod
    async def create(
        cls, data: dict, is_return_require: bool = False, out_dataclass: Optional[OuterGenericType] = None
    ) -> OuterGenericType | None:
        raise NotImplementedError

    @classmethod
    async def create_bulk(
        cls, items: List[dict], is_return_require: bool = False, out_dataclass: Optional[OuterGenericType] = None
    ) -> List[OuterGenericType] | None:
        raise NotImplementedError

    @classmethod
    async def update(
        cls,
        filter_data: dict,
        data: Dict[str, Any],
        is_return_require: bool = False,
        out_dataclass: Optional[OuterGenericType] = None,
    ) -> OuterGenericType | None:
        raise NotImplementedError

    @classmethod
    async def update_bulk(
        cls, items: List[dict], is_return_require: bool = False, out_dataclass: Optional[OuterGenericType] = None
    ) -> List[OuterGenericType] | None:
        raise NotImplementedError

    @classmethod
    async def update_or_create(
        cls,
        filter_data: dict,
        data: Dict[str, Any],
        is_return_require: bool = False,
        out_dataclass: Optional[OuterGenericType] = None,
    ) -> OuterGenericType | None:
        raise NotImplementedError

    @classmethod
    async def remove(
        cls,
        filter_data: dict,
    ) -> None:
        raise NotImplementedError

