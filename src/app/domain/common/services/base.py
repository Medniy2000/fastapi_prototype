from abc import ABC
from typing import Any, Dict, Generic, List, Optional, Tuple, Type

from src.app.core.repositories.base import AbstractBaseRepository, OuterGenericType


class AbstractBaseService(ABC):
    pass


class AbstractEntityService(AbstractBaseService, Generic[OuterGenericType]):
    @classmethod
    async def count(cls, filter_data: dict) -> int:
        raise NotImplementedError

    @classmethod
    async def is_exists(cls, filter_data: dict) -> bool:
        raise NotImplementedError

    @classmethod
    async def get_first(cls, filter_data: dict) -> OuterGenericType | None:
        raise NotImplementedError

    @classmethod
    async def get_list(
        cls, filter_data: dict, offset: int = 0, limit: Optional[int] = None, order_data: Tuple[str] = ("id",)
    ) -> List[OuterGenericType]:
        raise NotImplementedError

    @classmethod
    async def create(cls, data: dict, is_return_require: bool = False) -> OuterGenericType | None:
        raise NotImplementedError

    @classmethod
    async def create_bulk(
        cls, items: List[dict], is_return_require: bool = False
    ) -> List[OuterGenericType] | None:
        raise NotImplementedError

    @classmethod
    async def update(
        cls, filter_data: dict, data: Dict[str, Any], is_return_require: bool = False
    ) -> OuterGenericType | None:
        raise NotImplementedError

    @classmethod
    async def update_bulk(
        cls, items: List[dict], is_return_require: bool = False
    ) -> List[OuterGenericType] | None:
        raise NotImplementedError

    @classmethod
    async def update_or_create(
        cls, filter_data: dict, data: Dict[str, Any], is_return_require: bool = False
    ) -> OuterGenericType | None:
        raise NotImplementedError

    @classmethod
    async def remove(
        cls,
        filter_data: dict,
    ) -> None:
        raise NotImplementedError


class BaseEntityService(AbstractEntityService, Generic[OuterGenericType]):
    repository: Type[AbstractBaseRepository]

    @classmethod
    async def count(cls, filter_data: dict) -> int:
        return await cls.repository.count(filter_data=filter_data)

    @classmethod
    async def is_exists(cls, filter_data: dict) -> bool:
        return await cls.repository.is_exists(filter_data=filter_data)

    @classmethod
    async def get_first(cls, filter_data: dict) -> OuterGenericType | None:
        item = await cls.repository.get_first(filter_data=filter_data)
        return item

    @classmethod
    async def get_list(
        cls, filter_data: dict, offset: int = 0, limit: Optional[int] = None, order_data: Tuple[str] = ("id",)
    ) -> List[OuterGenericType]:
        filter_data_ = filter_data.copy()
        filter_data_["offset"] = offset
        if limit:
            filter_data_["limit"] = limit
        return await cls.repository.get_list(filter_data=filter_data_, order_data=order_data)

    @classmethod
    async def create(cls, data: dict, is_return_require: bool = False) -> OuterGenericType | None:
        return await cls.repository.create(data=data, is_return_require=is_return_require)

    @classmethod
    async def create_bulk(
        cls, items: List[dict], is_return_require: bool = False
    ) -> List[OuterGenericType] | None:
        return await cls.repository.create_bulk(items=items, is_return_require=is_return_require)

    @classmethod
    async def update(
        cls, filter_data: dict, data: Dict[str, Any], is_return_require: bool = False
    ) -> OuterGenericType | None:
        return await cls.repository.update(filter_data=filter_data, data=data, is_return_require=is_return_require)

    @classmethod
    async def update_bulk(
        cls, items: List[dict], is_return_require: bool = False
    ) -> List[OuterGenericType] | None:
        return await cls.repository.update_bulk(items=items, is_return_require=is_return_require)

    @classmethod
    async def update_or_create(
        cls, filter_data: dict, data: Dict[str, Any], is_return_require: bool = False
    ) -> OuterGenericType | None:
        return await cls.repository.update_or_create(
            filter_data=filter_data, data=data, is_return_require=is_return_require
        )

    @classmethod
    async def remove(
        cls,
        filter_data: dict,
    ) -> None:
        await cls.repository.remove(filter_data=filter_data)
