from abc import ABC
from copy import deepcopy
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from sqlalchemy import delete, exists, func, insert, inspect, select, Select, String, text, update

from src.app.core.utils.common import generate_str
from src.app.domain.core.aggregates.base import BaseAggregate
from src.app.extensions.psql_ext.psql_ext import Base, get_session

BaseModel = TypeVar("BaseModel", bound=Base)
OuterGenericType = TypeVar("OuterGenericType", bound=BaseAggregate)


class AbstractRepository(ABC):
    pass


class AbstractBaseRepository(AbstractRepository, Generic[OuterGenericType]):
    MODEL: Optional[Type[Base]] = None
    OUT_ENTITY: Optional[Type[BaseAggregate]] = None

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
    async def get_list(cls, filter_data: dict, order_data: Tuple[str] = ("id",)) -> List[OuterGenericType]:
        raise NotImplementedError

    @classmethod
    async def create(cls, data: dict, is_return_require: bool = False) -> OuterGenericType | None:
        raise NotImplementedError

    @classmethod
    async def create_bulk(cls, items: List[dict], is_return_require: bool = False) -> List[OuterGenericType] | None:
        raise NotImplementedError

    @classmethod
    async def update(
        cls, filter_data: dict, data: Dict[str, Any], is_return_require: bool = False
    ) -> OuterGenericType | None:
        raise NotImplementedError

    @classmethod
    async def update_bulk(cls, items: List[dict], is_return_require: bool = False) -> List[OuterGenericType] | None:
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


class BaseSQLAsyncDrivenBaseRepository(AbstractBaseRepository[OuterGenericType], Generic[OuterGenericType]):
    MODEL: Optional[Type[Base]] = None
    OUT_ENTITY: Optional[Type[BaseAggregate]] = None

    @staticmethod
    def __not_like_all(stmt: Any, k: Any, v: Any) -> Select:
        for item in v:
            stmt = stmt.filter(k.cast(String).like(f"%{str(item)}%"))
        return stmt

    @staticmethod
    def __jsonb_like(stmt: Any, key_1: Any, key_2: Any, v: Any) -> Select:
        if not key_2:
            return stmt.where(key_1.cast(String).like(f"%{v}%"))
        else:
            key_ = "jsonb_like" + generate_str(size=4)
            return stmt.where(
                text(f"{key_1}->>'{key_2}' LIKE CONCAT('%', CAST(:{key_} AS TEXT), '%')").params(**{key_: str(v)})
            )

    @staticmethod
    def __jsonb_not_like(stmt: Any, key_1: Any, key_2: Any, v: Any) -> Select:
        if not key_2:
            return stmt.where(~key_1.cast(String).like(f"%{v}%"))
        else:
            key_ = "jsonb_n_like" + generate_str(size=4)
            return stmt.where(
                text(f"{key_1}->>'{key_2}' NOT LIKE CONCAT('%', CAST(:{key_} AS TEXT), '%')").params(
                    **{key_: str(v)}
                )
            )

    __ATR_SEPARATOR: str = "__"
    LOOKUP_MAP = {
        "gt": lambda stmt, key1, _, v: stmt.where(key1 > v),
        "gte": lambda stmt, key1, _, v: stmt.where(key1 >= v),
        "lt": lambda stmt, key1, _, v: stmt.where(key1 < v),
        "lte": lambda stmt, key1, _, v: stmt.where(key1 <= v),
        "e": lambda stmt, key1, _, v: stmt.where(key1 == v),
        "ne": lambda stmt, key1, _, v: stmt.where(key1 != v),
        "in": lambda stmt, key1, _, v: stmt.where(key1.in_(v)),  # does not work with None
        "not_in": lambda stmt, key1, _, v: stmt.where(key1.not_in(v)),  # does not work with None
        "like": lambda stmt, key1, _, v: stmt.filter(key1.cast(String).like(f"%{str(v)}%")),
        "not_like_all": lambda stmt, key1, _, v: BaseSQLAsyncDrivenBaseRepository.__not_like_all(stmt, key1, v),
        "jsonb_like": lambda stmt, key1, key_2, v: BaseSQLAsyncDrivenBaseRepository.__jsonb_like(
            stmt, key1, key_2, v
        ),
        "jsonb_not_like": lambda stmt, key1, key_2, v: BaseSQLAsyncDrivenBaseRepository.__jsonb_not_like(
            stmt, key1, key_2, v
        ),
    }

    @classmethod
    def _parse_filter_key(cls, key: str) -> Tuple[str, str, str]:  # type: ignore
        splitted: list = key.split(cls.__ATR_SEPARATOR)

        if len(splitted) == 1:
            key_1 = splitted[0]
            key_2 = ""
            return key_1, key_2, "e"
        elif len(splitted) == 2:
            key_1 = splitted[0]
            key_2 = ""
            lookup = splitted[1]
            return key_1, key_2, lookup
        elif len(splitted) == 3:
            key_1 = splitted[0]
            key_2 = splitted[1]
            lookup = splitted[2]
            return key_1, key_2, lookup

    @classmethod
    def _parse_order_data(cls, order_data: Optional[Tuple[str]] = None) -> tuple:
        if not order_data:
            order_data = ()  # type: ignore
        parsed_order_data = []

        for order_item in order_data:  # type: ignore
            order_item_tmp = order_item
            if order_item_tmp.startswith("-"):
                order_item_tmp = order_item[1:]
                parsed_order_data.append(getattr(cls.model(), order_item_tmp).desc())
            else:
                parsed_order_data.append(getattr(cls.model(), order_item_tmp).asc())

        return tuple(parsed_order_data)

    @classmethod
    def _parse_order_data_for_target(cls, target: Base, order_data: Optional[Tuple[str]] = None) -> tuple:
        if not order_data:
            order_data = ()  # type: ignore
        parsed_order_data = []

        for order_item in order_data:  # type: ignore
            order_item_tmp = order_item
            if order_item_tmp.startswith("-"):
                order_item_tmp = order_item[1:]
                parsed_order_data.append(getattr(target, order_item_tmp).desc())
            else:
                parsed_order_data.append(getattr(target, order_item_tmp).asc())

        return tuple(parsed_order_data)

    @classmethod
    def _apply_where(cls, stmt: Any, filter_data: dict) -> Any:
        for key, value in filter_data.items():
            key_1, key_2, lookup = cls._parse_filter_key(key)
            key_1_ = getattr(cls.model(), key_1, None)
            key_2_ = key_2
            if "jsonb" in lookup and key_2:
                key_1_ = key_1
                key_2_ = key_2
            stmt = cls.LOOKUP_MAP[lookup](stmt, key_1_, key_2_, value)
        return stmt

    @classmethod
    def model(cls) -> Type[BaseModel]:
        if not cls.MODEL:
            raise AttributeError
        return cls.MODEL

    @classmethod
    def out_entity(cls) -> Callable:
        if not cls.OUT_ENTITY:
            raise AttributeError
        return cls.OUT_ENTITY

    @classmethod
    async def __get_max_id(cls) -> int:
        tmp_table_name = cls.model().__tablename__  # type: ignore
        max_id_stmp = f"SELECT MAX(t.id) FROM {tmp_table_name} t;"
        async with get_session(expire_on_commit=True) as session:
            max_id_q = await session.execute(statement=text(max_id_stmp))
            max_id = max_id_q.scalars().first() or 0
            return max_id

    @classmethod
    async def count(cls, filter_data: Optional[dict] = None) -> int:
        if not filter_data:
            filter_data = {}

        filter_data_ = deepcopy(filter_data)
        filter_data_.pop("limit", "")
        filter_data_.pop("offset", "")

        stmt: Select = select(func.count(cls.model().id))  # type: ignore
        stmt = cls._apply_where(stmt, filter_data=filter_data_)

        async with get_session(expire_on_commit=True) as session:
            result = await session.execute(stmt)
            return result.scalars().first()

    @classmethod
    async def is_exists(cls, filter_data: dict) -> bool:

        filter_data_ = deepcopy(filter_data)
        filter_data_.pop("limit", "")
        filter_data_.pop("offset", "")

        stmt = select(exists(cls.model()))
        stmt = cls._apply_where(stmt, filter_data=filter_data_)

        async with get_session() as session:
            result = await session.execute(stmt)
            is_exists = result.scalar() or False
            return is_exists

    @classmethod
    async def get_first(cls, filter_data: dict) -> OuterGenericType | None:
        filter_data_ = deepcopy(filter_data)
        filter_data_.pop("limit", "")
        filter_data_.pop("offset", "")

        stmt: Select = select(cls.model())
        stmt = cls._apply_where(stmt, filter_data=filter_data_)

        async with get_session(expire_on_commit=True) as session:
            result = await session.execute(stmt)

        raw = result.scalars().first()
        if raw:
            out_entity_ = cls.out_entity()
            entity_data_tmp = {c.key: getattr(raw, c.key) for c in inspect(raw).mapper.column_attrs}
            return out_entity_(**entity_data_tmp)
        return None

    @classmethod
    async def get_list(
        cls, filter_data: Optional[dict] = None, order_data: Optional[Tuple[str]] = ("id",)
    ) -> List[OuterGenericType]:
        if not filter_data:
            filter_data = {}
        limit = filter_data.pop("limit", None)
        offset = filter_data.pop("offset", 0)

        stmt: Select = select(cls.model())
        stmt = cls._apply_where(stmt, filter_data=filter_data)
        stmt = stmt.order_by(*cls._parse_order_data(order_data))
        stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        async with get_session(expire_on_commit=True) as session:
            result = await session.execute(stmt)

        raw_items = result.scalars().all()
        out_entity_ = cls.out_entity()

        items = []
        for i in raw_items:
            entity_data_tmp = {c.key: getattr(i, c.key) for c in inspect(i).mapper.column_attrs}
            items.append(out_entity_(**entity_data_tmp))
        return items

    @classmethod
    async def create(cls, data: dict, is_return_require: bool = False) -> OuterGenericType | None:

        async with get_session(expire_on_commit=True) as session:
            if "id" not in list(data.keys()):
                max_id = await cls.__get_max_id()
                data["id"] = max_id + 1

            if hasattr(cls.model(), "created_at") and "created_at" not in list(data.keys()):  # noqa
                data["created_at"] = datetime.utcnow()

            if hasattr(cls.model(), "updated_at") and "updated_at" not in list(data.keys()):
                data["updated_at"] = datetime.utcnow()

            id_ = data["id"]

            new_obj = cls.model()(**data)  # type: ignore
            session.add(new_obj)
            await session.commit()

        if is_return_require:
            item = await cls.get_first(filter_data={"id": id_})
            return item
        return None

    @classmethod
    async def create_bulk(cls, items: List[dict], is_return_require: bool = False) -> List[OuterGenericType] | None:
        if not items:
            return []

        max_id = await cls.__get_max_id()

        ids = []
        items_ = deepcopy(items)
        async with get_session(expire_on_commit=True) as session:

            for index, item in enumerate(items_):
                if item.get("id") is None or item.get("id", -1) < 0:
                    tmp_id = max_id + 1 + index
                    item["id"] = tmp_id

                dt = datetime.utcnow()
                if hasattr(cls.model(), "created_at") and "created_at" not in list(item.keys()):
                    item["created_at"] = dt

                if hasattr(cls.model(), "updated_at") and "updated_at" not in list(item.keys()):
                    item["updated_at"] = dt

                ids.append(item["id"])

            stmt = insert(cls.model()).values(items_)
            await session.execute(stmt)
            await session.flush()
            await session.commit()

        if is_return_require:
            items_to_return = await cls.get_list(filter_data={"id__in": ids}) or []
            sorted(items_to_return, key=lambda i: ids.index(i.id))  # type: ignore
            return items_to_return

        return None

    @classmethod
    async def update(
        cls, filter_data: dict, data: Dict[str, Any], is_return_require: bool = False
    ) -> OuterGenericType | None:

        stmt = update(cls.model())
        stmt = cls._apply_where(stmt, filter_data=filter_data)

        if hasattr(cls.model(), "updated_at") and "updated_at" not in list(data.keys()):
            data["updated_at"] = datetime.utcnow()

        stmt = stmt.values(**data)
        stmt.execution_options(synchronize_session="fetch")

        async with get_session(expire_on_commit=True) as session:
            await session.execute(stmt)
            await session.commit()

        if is_return_require:
            return await cls.get_first(filter_data=filter_data)
        return None

    @classmethod
    async def update_bulk(
        cls,
        items: List[dict],
        is_return_require: bool = False,
    ) -> List[OuterGenericType] | None:
        bind_param: str = "id"
        expire_on_commit = not is_return_require
        if items:
            async with get_session(expire_on_commit=expire_on_commit) as session:
                if hasattr(cls.model(), "updated_at"):
                    for i in items:
                        if "updated_at" not in list(i.keys()):
                            i["updated_at"] = datetime.utcnow()
                await session.execute(update(cls.model()), items)
                await session.flush()
                await session.commit()
            if is_return_require:
                params = [i.get(bind_param) for i in items]
                filter_data = {f"{bind_param}__in": params}
                items_ = await cls.get_list(filter_data=filter_data)
                sorted(items_, key=lambda el: params.index(getattr(el, bind_param, None)))  # type: ignore
                return items_
        return None

    @classmethod
    async def update_or_create(
        cls, filter_data: dict, data: Dict[str, Any], is_return_require: bool = False
    ) -> OuterGenericType | None:
        is_exists = await cls.is_exists(filter_data=filter_data)
        if is_exists:
            data_tmp = deepcopy(data)
            data_tmp.pop("id", None)
            data_tmp.pop("uuid", None)
            item = await cls.update(filter_data=filter_data, data=data_tmp, is_return_require=is_return_require)
            return item
        else:
            item = await cls.create(data=data, is_return_require=is_return_require)
            return item

    @classmethod
    async def remove(
        cls,
        filter_data: Dict[str, Any],
    ) -> None:
        if not filter_data:
            filter_data = {}
        stmt = delete(cls.model())
        stmt = cls._apply_where(stmt, filter_data=filter_data)

        async with get_session() as session:
            await session.execute(stmt)
            await session.commit()
