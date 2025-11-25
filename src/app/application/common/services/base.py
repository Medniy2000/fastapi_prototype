from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from src.app.infrastructure.repositories.base.abstract import AbstractBaseRepository


@dataclass
class BaseSvcOutEntity(ABC):
    pass

OutSvcGenericType = TypeVar("OutSvcGenericType", bound=BaseSvcOutEntity)

class AbstractBaseApplicationService(ABC):
    pass


class AbstractApplicationService(AbstractBaseApplicationService, Generic[OutSvcGenericType]):
    @classmethod
    async def count(cls, filter_data: dict) -> int:
        raise NotImplementedError

    @classmethod
    async def is_exists(cls, filter_data: dict) -> bool:
        raise NotImplementedError

    @classmethod
    async def get_first(
            cls,
            filter_data: dict,
            out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> OutSvcGenericType | None:
        raise NotImplementedError

    @classmethod
    async def get_list(
        cls,
            filter_data: dict,
            offset: int = 0,
            limit: Optional[int] = None,
            order_data: Tuple[str] = ("id",),
            out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> List[OutSvcGenericType]:
        raise NotImplementedError

    @classmethod
    async def create(
            cls,
            data: dict,
            is_return_require: bool = False,
            out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> OutSvcGenericType | None:
        raise NotImplementedError

    @classmethod
    async def create_bulk(
        cls,
        items: List[dict],
        is_return_require: bool = False,
        out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> List[OutSvcGenericType] | None:
        raise NotImplementedError

    @classmethod
    async def update(
        cls,
        filter_data: dict,
        data: Dict[str, Any],
        is_return_require: bool = False,
        out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> OutSvcGenericType | None:
        raise NotImplementedError

    @classmethod
    async def update_bulk(
        cls,
        items: List[dict],
        is_return_require: bool = False,
        out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> List[OutSvcGenericType] | None:
        raise NotImplementedError

    @classmethod
    async def update_or_create(
        cls,
        filter_data: dict,
        data: Dict[str, Any],
        is_return_require: bool = False,
        out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> OutSvcGenericType | None:
        raise NotImplementedError

    @classmethod
    async def remove(
        cls,
        filter_data: dict,
    ) -> None:
        raise NotImplementedError


class BaseApplicationService(AbstractApplicationService[OutSvcGenericType], Generic[OutSvcGenericType]):
    repository: Type[AbstractBaseRepository[OutSvcGenericType]]

    @classmethod
    async def count(cls, filter_data: dict) -> int:
        return await cls.repository.count(filter_data=filter_data)

    @classmethod
    async def is_exists(cls, filter_data: dict) -> bool:
        return await cls.repository.is_exists(filter_data=filter_data)

    @classmethod
    async def get_first(
            cls,
            filter_data: dict,
            out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> OutSvcGenericType | None:
        item = await cls.repository.get_first(filter_data=filter_data, out_dataclass=out_dataclass)
        return item

    @classmethod
    async def get_list(
        cls,
        filter_data: dict,
        offset: int = 0,
        limit: Optional[int] = None,
        order_data: Tuple[str] = ("id",),
        out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> List[OutSvcGenericType]:
        filter_data_ = filter_data.copy()
        filter_data_["offset"] = offset
        if limit is not None:
            filter_data_["limit"] = limit
        return await cls.repository.get_list(
            filter_data=filter_data_,
            order_data=order_data,
            out_dataclass=out_dataclass
        )

    @classmethod
    async def create(
            cls, data: dict,
            is_return_require: bool = False,
            out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> OutSvcGenericType | None:
        return await cls.repository.create(
            data=data,
            is_return_require=is_return_require,
            out_dataclass=out_dataclass
        )

    @classmethod
    async def create_bulk(
        cls,
        items: List[dict],
        is_return_require: bool = False,
        out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> List[OutSvcGenericType] | None:
        return await cls.repository.create_bulk(
            items=items,
            is_return_require=is_return_require,
            out_dataclass=out_dataclass
        )

    @classmethod
    async def update(
        cls,
        filter_data: dict,
        data: Dict[str, Any],
        is_return_require: bool = False,
        out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> OutSvcGenericType | None:
        return await cls.repository.update(
            filter_data=filter_data,
            data=data,
            is_return_require=is_return_require,
            out_dataclass=out_dataclass

        )

    @classmethod
    async def update_bulk(
        cls,
        items: List[dict],
        is_return_require: bool = False,
        out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> List[OutSvcGenericType] | None:
        return await cls.repository.update_bulk(
            items=items,
            is_return_require=is_return_require,
            out_dataclass=out_dataclass
        )

    @classmethod
    async def update_or_create(
        cls,
        filter_data: dict,
        data: Dict[str, Any],
        is_return_require: bool = False,
        out_dataclass: Optional[Type[OutSvcGenericType]] = None,
    ) -> OutSvcGenericType | None:
        return await cls.repository.update_or_create(
            filter_data=filter_data,
            data=data,
            is_return_require=is_return_require,
            out_dataclass=out_dataclass
        )

    @classmethod
    async def remove(
        cls,
        filter_data: dict,
    ) -> None:
        await cls.repository.remove(filter_data=filter_data)
