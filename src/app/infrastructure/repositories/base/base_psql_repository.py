import datetime as dt
from copy import deepcopy
from dataclasses import fields, make_dataclass
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, Type

from sqlalchemy import delete, exists, func, insert, inspect, select, Select, String, text, update, Column, JSON, \
    DateTime, Boolean, Float, Integer

from src.app.infrastructure.extensions.psql_ext.psql_ext import Base, get_session
from src.app.infrastructure.repositories.base.abstract import AbstractBaseRepository, OuterGenericType, BaseModel, \
    RepositoryError
from src.app.infrastructure.utils.common import generate_str


class PSQLLookupRegistry:
    LOOKUP_MAP = {
        "gt": lambda stmt, key1, _, v: PSQLLookupRegistry._greater_than(stmt, key1, v),
        "gte": lambda stmt, key1, _, v: PSQLLookupRegistry._greater_than_equal(stmt, key1, v),
        "lt": lambda stmt, key1, _, v: PSQLLookupRegistry._less_than(stmt, key1, v),
        "lte": lambda stmt, key1, _, v: PSQLLookupRegistry._less_than_equal(stmt, key1, v),
        "e": lambda stmt, key1, _, v: PSQLLookupRegistry._equal(stmt, key1, v),
        "ne": lambda stmt, key1, _, v: PSQLLookupRegistry._not_equal(stmt, key1, v),
        "in": lambda stmt, key1, _, v: PSQLLookupRegistry._in(stmt, key1, v),  # does not work with None
        "not_in": lambda stmt, key1, _, v: PSQLLookupRegistry._not_in(stmt, key1, v),  # does not work with None
        "ilike": lambda stmt, key1, _, v: PSQLLookupRegistry._ilike(stmt, key1, v),
        "like": lambda stmt, key1, _, v: PSQLLookupRegistry._like(stmt, key1, v),
        "not_like_all": lambda stmt, key1, _, v: PSQLLookupRegistry._not_like_all(stmt, key1, v),
        "jsonb_like": lambda stmt, key1, key_2, v: PSQLLookupRegistry._jsonb_like(stmt, key1, key_2, v),
        "jsonb_not_like": lambda stmt, key1, key_2, v: PSQLLookupRegistry._jsonb_not_like(stmt, key1, key_2, v),
    }
    _JSONB_LOOKUPS = ("jsonb_like", "jsonb_not_like", )


    @classmethod
    def get_operation(cls, name: str) -> Callable:
        """Get lookup operation by name"""
        operation = cls.LOOKUP_MAP.get(name, None)
        if not operation:
            raise RepositoryError(
                f"Unknown lookup operation: '{name}'. Available: {list(cls.LOOKUP_MAP.keys())}"
            )
        return operation

    @classmethod
    def apply_lookup(cls, stmt: Any, column: Any, lookup: str, value: Any, jsonb_field: str = None) -> Any:
        """Apply lookup operation to statement"""
        operation = cls.get_operation(lookup)

        if lookup in cls._JSONB_LOOKUPS:
            return operation(stmt, column, jsonb_field, value)
        else:
            return operation(stmt, column, jsonb_field, value)

    # Core lookup operations
    @staticmethod
    def _equal(stmt: Any, column: Any, value: Any) -> Any:
        """Equal comparison: column = value"""
        return stmt.where(column == value)

    @staticmethod
    def _not_equal(stmt: Any, column: Any, value: Any) -> Any:
        """Not equal comparison: column != value"""
        return stmt.where(column != value)

    @staticmethod
    def _greater_than(stmt: Any, column: Any, value: Any) -> Any:
        """Greater than comparison: column > value"""
        return stmt.where(column > value)

    @staticmethod
    def _greater_than_equal(stmt: Any, column: Any, value: Any) -> Any:
        """Greater than or equal comparison: column >= value"""
        return stmt.where(column >= value)

    @staticmethod
    def _less_than(stmt: Any, column: Any, value: Any) -> Any:
        """Less than comparison: column < value"""
        return stmt.where(column < value)

    @staticmethod
    def _less_than_equal(stmt: Any, column: Any, value: Any) -> Any:
        """Less than or equal comparison: column <= value"""
        return stmt.where(column <= value)

    @staticmethod
    def _in(stmt: Any, column: Any, value: List[Any]) -> Any:
        """IN comparison: column IN (values)"""
        if not isinstance(value, (list, tuple)):
            raise RepositoryError("IN lookup requires list or tuple value")
        return stmt.where(column.in_(value))

    @staticmethod
    def _not_in(stmt: Any, column: Any, value: List[Any]) -> Any:
        """NOT IN comparison: column NOT IN (values)"""
        if not isinstance(value, (list, tuple)):
            raise RepositoryError("NOT_IN lookup requires list or tuple value")
        return stmt.where(column.not_in(value))

    @staticmethod
    def _like(stmt: Any, column: Any, value: Any) -> Any:
        """LIKE comparison: column LIKE %value%"""
        return stmt.filter(column.cast(String).like(f"%{str(value)}%"))

    @staticmethod
    def _ilike(stmt: Any, column: Any, value: Any) -> Any:
        """LIKE comparison: column LIKE %value%"""
        return stmt.filter(column.cast(String).ilike(f"%{str(value)}%"))

    @staticmethod
    def _not_like_all(stmt: Any, column: Any, value: List[str]) -> Select:
        """NOT LIKE ALL: column NOT LIKE ALL values (all values must not match)"""
        if not isinstance(value, (list, tuple)):
            raise RepositoryError("NOT_LIKE_ALL lookup requires list or tuple value")

        for item in value:
            stmt = stmt.filter(column.cast(String).like(f"%{str(item)}%"))
        return stmt

    @staticmethod
    def _jsonb_like(stmt: Any, key_1: Any, key_2: Any, v: Any) -> Select:
        if not key_2:
            return stmt.where(key_1.cast(String).like(f"%{v}%"))
        else:
            key_ = "jsonb_like" + generate_str(size=4)
            return stmt.where(
                text(f"{key_1}->>'{key_2}' LIKE CONCAT('%', CAST(:{key_} AS TEXT), '%')").params(**{key_: str(v)})
            )

    @staticmethod
    def _jsonb_not_like(stmt: Any, key_1: Any, key_2: Any, v: Any) -> Select:
        if not key_2:
            return stmt.where(~key_1.cast(String).like(f"%{v}%"))
        else:
            key_ = "jsonb_n_like" + generate_str(size=4)
            return stmt.where(
                text(f"{key_1}->>'{key_2}' NOT LIKE CONCAT('%', CAST(:{key_} AS TEXT), '%')").params(
                    **{key_: str(v)}
                )
            )


class QueryBuilder:
    LOOKUP_REGISTRY_CLASS = PSQLLookupRegistry

    __ATR_SEPARATOR: str = "__"
    PAGINATION_KEYS = ["limit", "offset"]
    _MODEL_COLUMNS_CACHE: Dict[str, Dict[str, Column]] = {}

    @classmethod
    def lookup_registry(cls) -> Type[PSQLLookupRegistry]:
        return cls.LOOKUP_REGISTRY_CLASS

    @classmethod
    def _get_model_columns(cls, model_class: Type[Base]) -> Dict[str, Column]:
        """Get all columns from the model with caching"""
        model_name = model_class.__name__

        if model_name not in cls._MODEL_COLUMNS_CACHE:
            inspector = inspect(model_class)
            cls._MODEL_COLUMNS_CACHE[model_name] = {col.name: col for col in inspector.columns}

        return cls._MODEL_COLUMNS_CACHE[model_name]

    @classmethod
    def validate_filter_value(cls, column: Column, key, value:Any, lookup: str) -> None:
        """Validate filter data before building query"""
        # Handle None values
        if value is None and not column.nullable:
            raise RepositoryError(f"Column '{key}' cannot be None (not nullable)")

        if value is None:
            return  # None is valid for nullable columns

        column_type = column.type

        # For list-based lookups, validate each item
        if lookup in ('in', 'not_in') and isinstance(value, (list, tuple)):
            for item in value:
                if item is not None:
                    cls._validate_single_value_type(key, item, column_type)
            return

        # For operations that convert to string, be more lenient
        if lookup in ('not_like_all', 'like', 'jsonb_like', 'jsonb_not_like'):
            if lookup == 'not_like_all':
                if not isinstance(value, (list, tuple)):
                    raise RepositoryError(f"Lookup 'not_like_all' for column '{key}' requires list/tuple value")
            # These operations convert values to strings, so accept any convertible type
            return

        cls._validate_single_value_type(key, value, column_type)

    @classmethod
    def _validate_single_value_type(cls, key: str, value: Any, column_type: Any) -> None:
        """Validate a single value against column type"""
        # String types (including TEXT, VARCHAR, etc.)
        if isinstance(column_type, String):
            if not isinstance(value, str):
                raise RepositoryError(f"Column '{key}' expects string value, got {type(value).__name__}")

        # Integer types
        elif isinstance(column_type, Integer):
            if not isinstance(value, int):
                raise RepositoryError(f"Column '{key}' expects integer value, got {type(value).__name__}")

        # Float types
        elif isinstance(column_type, Float):
            if not isinstance(value, (int, float)):
                raise RepositoryError(f"Column '{key}' expects numeric value, got {type(value).__name__}")

        # Boolean types
        elif isinstance(column_type, Boolean):
            if not isinstance(value, bool):
                raise RepositoryError(f"Column '{key}' expects boolean value, got {type(value).__name__}")

        # DateTime types
        elif isinstance(column_type, DateTime):
            from datetime import datetime
            if not isinstance(value, datetime):
                raise RepositoryError(f"Column '{key}' expects datetime value, got {type(value).__name__}")

        # JSON/JSONB types
        elif isinstance(column_type, JSON):
            # JSON can accept various types, so we're more lenient
            if not isinstance(value, (dict, list, str, int, float, bool)):
                raise RepositoryError(f"Column '{key}' expects JSON-compatible value, got {type(value).__name__}")

    @classmethod
    def validate_model_key(cls, key: str, model_class:Type[Base]) -> Column:
        column_ = cls._get_model_columns(model_class).get(key, None)
        if column_ is None:
            raise RepositoryError(f"Column '{key}' does not exist in model {model_class.__name__}")
        return column_

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
    def apply_where(
            cls,
            stmt: Any,
            filter_data: Optional[Dict[str, Any]],
            model_class: Type[Base]
    ) -> Any:
        if not filter_data:
            return stmt

        for key, value in filter_data.items():
            if key in cls.PAGINATION_KEYS:
                continue
            c_name, c_jsonb_name, lookup = cls._parse_filter_key(key)

            column_ = cls.validate_model_key(c_name, model_class)
            cls.validate_filter_value(column_, key, value, lookup)

            stmt = cls.lookup_registry().apply_lookup(
                stmt=stmt,
                column=column_,
                lookup=lookup,
                value=value,
                jsonb_field=c_jsonb_name
            )
        return stmt

    @classmethod
    def apply_ordering(
            cls,
            stmt: Any,
            order_data: Optional[Tuple[str, ...]],
            model_class:Type[Base]
    ) -> Any:
        """Apply ORDER BY clause to statement"""
        if not order_data:
            return stmt

        try:
            parsed_order = cls._parse_order_data(order_data, model_class)
            return stmt.order_by(*parsed_order)
        except Exception as e:
            raise RepositoryError(f"Failed to apply ordering: {str(e)}")

    @classmethod
    def apply_pagination(cls, stmt: Any, filter_data: Optional[Dict[str, Any]] = None) -> Any:
        """Apply LIMIT and OFFSET to statement"""
        if not filter_data:
            return stmt

        # Extract pagination parameters
        limit = filter_data.get("limit")
        offset = filter_data.get("offset", 0)

        # Apply offset
        if offset:
            if not isinstance(offset, int) or offset < 0:
                raise RepositoryError(f"Offset must be non-negative integer, got: {offset}")
            stmt = stmt.offset(offset)

        # Apply limit
        if limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                raise RepositoryError(f"Limit must be positive integer, got: {limit}")
            stmt = stmt.limit(limit)

        return stmt

    @classmethod
    def _parse_order_data(
        cls,
        order_data: Tuple[str, ...],
        model_class: Type[Base]
    ) -> List[Any]:
        """Parse order data into SQLAlchemy order clauses"""
        parsed_order = []

        for order_item in order_data:
            if not isinstance(order_item, str):
                raise RepositoryError(f"Order field must be string, got: {type(order_item).__name__}")

            # Handle descending order (prefix with -)
            if order_item.startswith("-"):
                field_name = order_item[1:]
                direction = "desc"
            else:
                field_name = order_item
                direction = "asc"

            # Validate field exists in model
            try:
                column_ = cls.validate_model_key(field_name, model_class)
                parsed_order.append(getattr(column_, direction)())
            except Exception as e:
                raise RepositoryError(f"Invalid order field '{field_name}': {str(e)}")

        return parsed_order





class BasePSQLRepository(AbstractBaseRepository[OuterGenericType], Generic[OuterGenericType]):
    MODEL: Optional[Type[Base]] = None
    _QUERY_BUILDER_CLASS: Type[QueryBuilder] = QueryBuilder

    @classmethod
    def query_builder(cls) -> Type[QueryBuilder]:
        if not cls._QUERY_BUILDER_CLASS:
            raise AttributeError
        return cls._QUERY_BUILDER_CLASS

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

        # Only deep copy if filter_data will be modified
        filter_data_ = filter_data.copy() if filter_data else {}

        stmt: Select = select(func.count(cls.model().id))  # type: ignore
        stmt = cls.query_builder().apply_where(
            stmt,
            filter_data=filter_data_,
            model_class=cls.model()
        )

        async with get_session(expire_on_commit=True) as session:
            result = await session.execute(stmt)
            return result.scalars().first()

    @classmethod
    async def is_exists(cls, filter_data: dict) -> bool:

        filter_data_ = filter_data.copy()

        stmt = select(exists(cls.model()))
        stmt = cls.query_builder().apply_where(
            stmt,
            filter_data=filter_data_,
            model_class=cls.model()
        )

        async with get_session() as session:
            result = await session.execute(stmt)
            is_exists = result.scalar() or False
            return is_exists

    @classmethod
    async def get_first(
        cls, filter_data: dict, out_dataclass: Optional[OuterGenericType] = None
    ) -> OuterGenericType | None:
        filter_data_ = filter_data.copy()

        stmt: Select = select(cls.model())
        stmt = cls.query_builder().apply_where(
            stmt,
            filter_data=filter_data_,
            model_class=cls.model()
        )

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
        filter_data_ = filter_data.copy()

        stmt: Select = select(cls.model())
        stmt = cls.query_builder().apply_where(
            stmt,
            filter_data=filter_data_,
            model_class=cls.model()
        )
        stmt = cls.query_builder().apply_ordering(
            stmt,
            order_data=order_data,
            model_class=cls.model()
        )
        stmt = cls.query_builder().apply_pagination(
            stmt,
            filter_data=filter_data_
        )

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

        # Normalize data to handle mixed completeness
        cls._normalize_bulk_data(items=items_copy)

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
        data_copy = data.copy()

        stmt = update(cls.model())
        stmt = cls.query_builder().apply_where(
            stmt,
            filter_data=filter_data,
            model_class=cls.model()
        )

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
    def _normalize_bulk_data(cls, items: List[dict]) -> None:
        """Normalize bulk data to handle mixed field completeness"""
        if not items:
            return

        # Get all unique keys from all items
        all_keys: set[str] = set()
        for item in items:
            all_keys.update(item.keys())

        # Get model column defaults and nullable info
        model_class = cls.model()  # type: ignore
        model_table = model_class.__table__  # type: ignore

        # For each item, ensure it has all fields with appropriate defaults
        for item in items:
            for key in all_keys:
                if key not in item:
                    # Check if column exists in model
                    if hasattr(model_class, key):
                        column = getattr(model_table.c, key, None)
                        if column is not None:
                            # Only add explicit None if column is nullable and has no default
                            if column.nullable and column.default is None and column.server_default is None:
                                item[key] = None
                            # Don't add anything for columns with defaults - let database handle it

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
            item = await cls.update(
                filter_data=filter_data,
                data=data_tmp,
                is_return_require=is_return_require,
                out_dataclass=out_dataclass,
            )
            return item
        else:
            item = await cls.create(data=data, is_return_require=is_return_require, out_dataclass=out_dataclass)
            return item

    @classmethod
    async def remove(
        cls,
        filter_data: Dict[str, Any],
    ) -> None:
        if not filter_data:
            filter_data = {}
        stmt = delete(cls.model())
        stmt = cls.query_builder().apply_where(
            stmt,
            filter_data=filter_data,
            model_class=cls.model()
        )

        async with get_session() as session:
            await session.execute(stmt)
            await session.commit()
