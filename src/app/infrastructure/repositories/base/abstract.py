from abc import ABC
from copy import deepcopy
import datetime as dt
from dataclasses import dataclass, fields, make_dataclass
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from sqlalchemy import delete, exists, func, insert, inspect, select, Select, String, text, update

from src.app.infrastructure.utils.common import generate_str
from src.app.infrastructure.extensions.psql_ext.psql_ext import Base, get_session


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


class BasePSQLRepository(AbstractBaseRepository[OuterGenericType], Generic[OuterGenericType]):
    MODEL: Optional[Type[Base]] = None

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
        "not_like_all": lambda stmt, key1, _, v: BasePSQLRepository.__not_like_all(stmt, key1, v),
        "jsonb_like": lambda stmt, key1, key_2, v: BasePSQLRepository.__jsonb_like(stmt, key1, key_2, v),
        "jsonb_not_like": lambda stmt, key1, key_2, v: BasePSQLRepository.__jsonb_not_like(stmt, key1, key_2, v),
    }

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
    def __make_out_dataclass(cls) -> Tuple[Callable, List[str]]:
        model = cls.model()  # type: ignore
        columns = inspect(model).c
        field_names = [column.name for column in columns]
        field_types = {column.name: column.type.python_type for column in columns}

        # Dynamically create a dataclass using `make_dataclass`
        dataclass_name = model.__name__ + "Entity"

        # Generate the dataclass with the field names and types
        dataclass_fields = [(name, field_types[name]) for name in field_names]
        dynamic_dataclass = make_dataclass(dataclass_name, dataclass_fields)

        return dynamic_dataclass, field_names

    @classmethod
    def out_dataclass_with_columns(
        cls, out_dataclass: Optional[OuterGenericType] = None
    ) -> Tuple[Callable, List[str]]:
        if not out_dataclass:
            out_dataclass_, columns = cls.__make_out_dataclass()
        else:
            out_dataclass_ = out_dataclass  # type: ignore
            columns = [f.name for f in fields(out_dataclass_)]  # type: ignore

        return out_dataclass_, columns

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
    async def get_first(
        cls, filter_data: dict, out_dataclass: Optional[OuterGenericType] = None
    ) -> OuterGenericType | None:
        filter_data_ = deepcopy(filter_data)
        filter_data_.pop("limit", "")
        filter_data_.pop("offset", "")

        stmt: Select = select(cls.model())
        stmt = cls._apply_where(stmt, filter_data=filter_data_)

        async with get_session(expire_on_commit=True) as session:
            result = await session.execute(stmt)

        raw = result.scalars().first()
        if raw:
            out_entity_, _ = cls.out_dataclass_with_columns(out_dataclass=out_dataclass)
            entity_data_tmp = {c.key: getattr(raw, c.key) for c in inspect(raw).mapper.column_attrs}
            return out_entity_(**entity_data_tmp)
        return None

    @classmethod
    async def get_list(
        cls,
        filter_data: Optional[dict] = None,
        order_data: Optional[Tuple[str]] = ("id",),
        out_dataclass: Optional[OuterGenericType] = None,
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

        items = []
        out_entity_, _ = cls.out_dataclass_with_columns(out_dataclass=out_dataclass)
        for i in raw_items:
            entity_data_tmp = {c.key: getattr(i, c.key) for c in inspect(i).mapper.column_attrs}
            items.append(out_entity_(**entity_data_tmp))
        return items

    @classmethod
    async def create(
        cls, data: dict, is_return_require: bool = False, out_dataclass: Optional[OuterGenericType] = None
    ) -> OuterGenericType | None:
        data_copy = data.copy()

        # Handle explicit ID if provided, otherwise let database auto-increment
        explicit_id_provided = "id" in data_copy and data_copy["id"] is not None

        cls._set_timestamps_on_create(items=[data_copy])

        async with get_session(expire_on_commit=True) as session:
            if is_return_require:
                # Use RETURNING to get specific columns instead of the whole model
                model_class = cls.model()  # type: ignore
                model_table = model_class.__table__  # type: ignore
                stmt = insert(model_class).values(data_copy).returning(*model_table.columns.values())
                result = await session.execute(stmt)
                await session.commit()
                raw = result.fetchone()
                if raw:
                    out_entity_, _ = cls.out_dataclass_with_columns(out_dataclass=out_dataclass)
                    # Convert Row to dict using column names
                    entity_data = dict(zip([col.name for col in model_table.columns.values()], raw))
                    return out_entity_(**entity_data)
            else:
                if explicit_id_provided:
                    # For explicit ID, use insert statement to handle potential conflicts better
                    await session.execute(insert(cls.model()).values(data_copy))
                else:
                    # For auto-increment ID, use ORM method
                    new_obj = cls.model()(**data_copy)  # type: ignore
                    session.add(new_obj)
                await session.commit()

        return None

    @classmethod
    async def create_bulk(
        cls, items: List[dict], is_return_require: bool = False, out_dataclass: Optional[OuterGenericType] = None
    ) -> List[OuterGenericType] | None:
        if not items:
            return []

        items_copy = deepcopy(items)

        # Add timestamps to all items
        cls._set_timestamps_on_create(items=items_copy)

        async with get_session(expire_on_commit=True) as session:
            model_class = cls.model()  # type: ignore
            model_table = model_class.__table__  # type: ignore
            if is_return_require:
                # Use RETURNING to get created records efficiently
                stmt = insert(model_class).values(items_copy).returning(*model_table.columns.values())
                result = await session.execute(stmt)
                await session.commit()

                raw_items = result.fetchall()
                out_entity_, _ = cls.out_dataclass_with_columns(out_dataclass=out_dataclass)
                created_items = []
                column_names = [col.name for col in model_table.columns.values()]
                for raw in raw_items:
                    # Convert Row to dict using column names
                    entity_data = dict(zip(column_names, raw))
                    created_items.append(out_entity_(**entity_data))
                return created_items
            else:
                await session.execute(insert(model_class).values(items_copy))
                await session.commit()

        return None

    @classmethod
    async def update(
        cls,
        filter_data: dict,
        data: Dict[str, Any],
        is_return_require: bool = False,
        out_dataclass: Optional[OuterGenericType] = None,
    ) -> OuterGenericType | None:
        data_copy = deepcopy(data)

        stmt = update(cls.model())
        stmt = cls._apply_where(stmt, filter_data=filter_data)

        cls._set_timestamps_on_update(items=[data_copy])

        stmt = stmt.values(**data_copy)
        stmt.execution_options(synchronize_session="fetch")

        async with get_session(expire_on_commit=True) as session:
            await session.execute(stmt)
            await session.commit()

        if is_return_require:
            return await cls.get_first(filter_data=filter_data, out_dataclass=out_dataclass)
        return None

    @classmethod
    async def _update_single_with_returning(
        cls, session: Any, item_data: dict, out_entity_: Callable
    ) -> OuterGenericType | None:
        """Update a single item and return the updated entity"""
        if "id" not in item_data:
            return None

        model_class = cls.model()  # type: ignore
        model_table = model_class.__table__  # type: ignore

        item_id = item_data.pop("id")
        stmt = (
            update(model_class)
            .where(model_class.id == item_id)  # type: ignore
            .values(**item_data)
            .returning(*model_table.columns.values())
        )
        result = await session.execute(stmt)
        raw = result.fetchone()
        if raw:
            # Convert Row to dict using column names
            column_names = [col.name for col in model_table.columns.values()]
            entity_data = dict(zip(column_names, raw))
            return out_entity_(**entity_data)
        return None

    @classmethod
    async def update_bulk(
        cls, items: List[dict], is_return_require: bool = False, out_dataclass: Optional[OuterGenericType] = None
    ) -> List[OuterGenericType] | None:
        if not items:
            return None

        items_copy = deepcopy(items)

        cls._set_timestamps_on_update(items=items_copy)

        async with get_session(expire_on_commit=True) as session:
            if is_return_require:
                return await cls._bulk_update_with_returning(session, items_copy, out_dataclass)
            else:
                await cls._bulk_update_without_returning(session, items_copy)
                return None

    @classmethod
    def _set_timestamps_on_update(cls, items: List[dict]) -> None:
        """Set updated_at on update"""
        if hasattr(cls.model(), "updated_at"):
            dt_ = dt.datetime.now(dt.UTC).replace(tzinfo=None)
            for item in items:
                if "updated_at" not in item:
                    item["updated_at"] = dt_

    @classmethod
    def _set_timestamps_on_create(cls, items: List[dict]) -> None:
        """Set created_at, updated_at on create"""
        if hasattr(cls.model(), "updated_at") or hasattr(cls.model(), "created_at"):
            dt_ = dt.datetime.now(dt.UTC).replace(tzinfo=None)
            for item in items:
                if hasattr(cls.model(), "updated_at") and "updated_at" not in item:
                    item["updated_at"] = dt_
                if hasattr(cls.model(), "created_at") and "created_at" not in item:
                    item["created_at"] = dt_

    @classmethod
    async def _bulk_update_with_returning(
        cls, session: Any, items: List[dict], out_dataclass: Optional[OuterGenericType] = None
    ) -> List[OuterGenericType]:
        """Perform bulk update with RETURNING for result collection"""
        updated_items = []
        out_entity_, _ = cls.out_dataclass_with_columns(out_dataclass=out_dataclass)

        for item_data in items:
            updated_item = await cls._update_single_with_returning(session, item_data, out_entity_)
            if updated_item:
                updated_items.append(updated_item)

        await session.commit()
        return updated_items

    @classmethod
    async def _bulk_update_without_returning(cls, session: Any, items: List[dict]) -> None:
        """Perform bulk update without RETURNING for better performance"""
        await session.execute(update(cls.model()), items)
        await session.commit()

    @classmethod
    async def update_or_create(
        cls,
        filter_data: dict,
        data: Dict[str, Any],
        is_return_require: bool = False,
        out_dataclass: Optional[OuterGenericType] = None,
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
