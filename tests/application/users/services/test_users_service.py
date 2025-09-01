import uuid
from asyncio import AbstractEventLoop
from copy import deepcopy
from datetime import datetime
from typing import Any, List, Type

import pytest

from src.app.core.utils.common import generate_str
from src.app.core.repositories.users_repository import UserAggregate
from src.app.application.container import container as service_container
from tests.fixtures.constants import USERS


def test_users_count(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service
    count = e_loop.run_until_complete(users_service.count(filter_data={}))
    assert isinstance(count, int)
    assert count == len(USERS)


def test_users_count_empty(e_loop: AbstractEventLoop) -> None:
    users_service = service_container.users_service
    count = e_loop.run_until_complete(users_service.count(filter_data={}))
    assert isinstance(count, int)
    assert count == 0


def test_users_repository_get_first_by_attr_name(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service
    attr_names = ["id", "uuid", "email"]
    for user_raw in USERS:
        for attr_name in attr_names:
            user: Type[UserAggregate] | None = e_loop.run_until_complete(
                users_service.get_first(filter_data={attr_name: user_raw.get(attr_name)})
            )
            assert isinstance(user, UserAggregate) is True
            for key, value in user_raw.items():
                assert getattr(user, key) == value


def test_users_get_list_basic(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service
    items: List[Type[UserAggregate]] = e_loop.run_until_complete(users_service.get_list(filter_data={}))
    assert isinstance(items, list) is True
    assert len(items) == len(USERS)
    raw_ids = [i["id"] for i in USERS]
    for user in items:
        assert isinstance(user, UserAggregate) is True
        assert user.id in raw_ids


def test_users_repository_create(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    user_data_raw = {
        "id": 999,
        "uuid": uuid.uuid4().__str__(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "meta": {
            "first_name": "first_name_n",
            "last_name": "last_name_n",
        },
        "birthday": datetime.utcnow(),
        "is_active": True,
        "first_name": "first_name_n",
        "last_name": "last_name_n",
        "email": "n" + generate_str(5) + "@gmail.com",
    }
    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))
    created_user: UserAggregate | None = e_loop.run_until_complete(
        users_service.create(data=user_data_raw, is_return_require=True)
    )
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    assert isinstance(created_user, UserAggregate) is True
    for key, value in user_data_raw.items():
        assert getattr(created_user, key) == value
    assert count_after == count_before + 1


def test_users_repository_create_without_id_and_uuid(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    user_data_raw = {
        "meta": {
            "first_name": "first_name_n",
            "last_name": "last_name_n",
        },
        "birthday": datetime.utcnow(),
        "is_active": True,
        "first_name": "first_name_n",
        "last_name": "last_name_n",
        "email": "n" + generate_str(5) + "@gmail.com",
    }
    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))
    created_user: UserAggregate | None = e_loop.run_until_complete(
        users_service.create(data=user_data_raw, is_return_require=True)
    )
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    assert isinstance(created_user, UserAggregate) is True

    assert getattr(created_user, "id") is not None
    assert getattr(created_user, "uuid") is not None
    for key, value in user_data_raw.items():
        assert getattr(created_user, key) == value
    assert count_after == count_before + 1


def test_users_repository_create_is_not_return(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    user_data_raw = {
        "meta": {
            "first_name": "first_name_n",
            "last_name": "last_name_n",
        },
        "birthday": datetime.utcnow(),
        "is_active": True,
        "first_name": "first_name_n",
        "last_name": "last_name_n",
        "email": "n" + generate_str(5) + "@gmail.com",
    }
    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))
    created_user: UserAggregate | None = e_loop.run_until_complete(
        users_service.create(data=user_data_raw, is_return_require=False)
    )
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    assert created_user is None

    assert count_after == count_before + 1


def test_users_repository_create_bulk(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    user_data_raw_1 = {
        "id": 998,
        "uuid": uuid.uuid4().__str__(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "meta": {
            "first_name": "first_name_n1",
            "last_name": "last_name_n1",
        },
        "birthday": datetime.utcnow(),
        "is_active": True,
        "first_name": "first_name_n1",
        "last_name": "last_name_n1",
        "email": "n1" + generate_str(5) + "@gmail.com",
    }
    user_data_raw_2 = {
        "id": 999,
        "uuid": uuid.uuid4().__str__(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "meta": {
            "first_name": "first_name_n2",
            "last_name": "last_name_n2",
        },
        "birthday": datetime.utcnow(),
        "is_active": True,
        "first_name": "first_name_n2",
        "last_name": "last_name_n2",
        "email": "n2" + generate_str(5) + "@gmail.com",
    }
    items_raw = [user_data_raw_1, user_data_raw_2]

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))
    created_items: List[UserAggregate] | None = e_loop.run_until_complete(
        users_service.create_bulk(items=items_raw, is_return_require=True)
    )
    created_items = created_items or []
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    for index, created_user in enumerate(created_items):
        assert isinstance(created_user, UserAggregate) is True
        user_data_raw = items_raw[index]
        for key, value in user_data_raw.items():
            assert getattr(created_user, key) == value

    assert count_after == count_before + len(items_raw)


def test_users_repository_create_bulk_without_id_uuid(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    user_data_raw_1 = {
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "meta": {
            "first_name": "first_name_n1",
            "last_name": "last_name_n1",
        },
        "birthday": datetime.utcnow(),
        "is_active": True,
        "first_name": "first_name_n1",
        "last_name": "last_name_n1",
        "email": "n1" + generate_str(5) + "@gmail.com",
    }
    user_data_raw_2 = {
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "meta": {
            "first_name": "first_name_n2",
            "last_name": "last_name_n2",
        },
        "birthday": datetime.utcnow(),
        "is_active": True,
        "first_name": "first_name_n2",
        "last_name": "last_name_n2",
        "email": "n2" + generate_str(5) + "@gmail.com",
    }
    items_raw = [user_data_raw_1, user_data_raw_2]

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))
    created_items: List[UserAggregate] | None = e_loop.run_until_complete(
        users_service.create_bulk(items=items_raw, is_return_require=True)
    )
    created_items = created_items or []
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    for index, created_user in enumerate(created_items):
        assert isinstance(created_user, UserAggregate) is True
        user_data_raw = items_raw[index]
        assert getattr(created_user, "id") is not None
        assert getattr(created_user, "uuid") is not None
        for key, value in user_data_raw.items():
            assert getattr(created_user, key) == value

    assert count_after == count_before + len(items_raw)


def test_users_repository_create_bulk_is_not_return(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    user_data_raw_1 = {
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "meta": {
            "first_name": "first_name_n1",
            "last_name": "last_name_n1",
        },
        "birthday": datetime.utcnow(),
        "is_active": True,
        "first_name": "first_name_n1",
        "last_name": "last_name_n1",
        "email": "n1" + generate_str(5) + "@gmail.com",
    }
    user_data_raw_2 = {
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "meta": {
            "first_name": "first_name_n2",
            "last_name": "last_name_n2",
        },
        "birthday": datetime.utcnow(),
        "is_active": True,
        "first_name": "first_name_n2",
        "last_name": "last_name_n2",
        "email": "n2" + generate_str(5) + "@gmail.com",
    }
    items_raw = [user_data_raw_1, user_data_raw_2]

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))
    created_items: List[UserAggregate] | None = e_loop.run_until_complete(
        users_service.create_bulk(items=items_raw, is_return_require=False)
    )
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    assert created_items is None
    assert count_after == count_before + len(items_raw)


def test_users_repository_update_full(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    user_data_raw = deepcopy(USERS[0])
    val_to_update = "updated_first_name"
    user_data_raw["first_name"] = val_to_update

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))  # noqa
    updated_user: UserAggregate | None = e_loop.run_until_complete(
        users_service.update(filter_data={"id": user_data_raw["id"]}, data=user_data_raw, is_return_require=True)
    )
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    assert isinstance(updated_user, UserAggregate) is True
    for key, value in user_data_raw.items():
        assert getattr(updated_user, key) == value
    assert count_after == count_before


def test_users_repository_update_partial(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    user_data = deepcopy(USERS[0])
    user_data_raw = {
        "updated_at": datetime.utcnow(),
        "first_name": "updated_first_name_1",
        "last_name": "updated_last_name_1",
    }

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))  # noqa
    updated_user: UserAggregate | None = e_loop.run_until_complete(
        users_service.update(filter_data={"id": user_data["id"]}, data=user_data_raw, is_return_require=True)
    )
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    assert isinstance(updated_user, UserAggregate) is True
    for key, value in user_data.items():
        val_updated = getattr(updated_user, key)
        if key in user_data_raw:
            value = user_data_raw.get(key, None)
        assert val_updated == value
    assert count_after == count_before


def test_users_repository_update_without_return(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    user_data = deepcopy(USERS[0])
    user_data_raw = {
        "updated_at": datetime.utcnow(),
        "first_name": "updated_first_name_1",
        "last_name": "updated_last_name_1",
    }

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))  # noqa
    updated_user: UserAggregate | None = e_loop.run_until_complete(
        users_service.update(filter_data={"id": user_data["id"]}, data=user_data_raw, is_return_require=False)
    )
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    assert updated_user is None
    assert count_after == count_before


def test_users_repository_bulk_update_full(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    item_1_to_update = deepcopy(USERS[0])
    item_2_to_update = deepcopy(USERS[1])

    item_1_to_update["first_name"] = "updated_1_first_name"
    item_2_to_update["first_name"] = "updated_2_first_name"

    items_to_update = [item_1_to_update, item_2_to_update]

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))  # noqa
    updated_items: List[Type[UserAggregate]] | None = e_loop.run_until_complete(
        users_service.update_bulk(items=items_to_update, is_return_require=True)
    )
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    assert isinstance(updated_items, list) is True

    for user_data_raw in items_to_update:
        id_ = user_data_raw["id"]
        updated_items = updated_items or []
        updated_items_tmp = [i for i in updated_items if i.id == id_]
        updated_user = None
        if updated_items_tmp:
            updated_user = updated_items_tmp[0]
        for key, value in user_data_raw.items():
            assert getattr(updated_user, key, None) == value
    assert count_after == count_before


def test_users_repository_bulk_update_partial(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    item_1_to_update = {
        "id": USERS[0]["id"],
        "uuid": str(USERS[0]["uuid"]),
        "updated_at": datetime.utcnow(),
        "first_name": "updated_1_first_name",
    }
    item_2_to_update = {
        "id": USERS[1]["id"],
        "uuid": str(USERS[1]["uuid"]),
        "updated_at": datetime.utcnow(),
        "first_name": "updated_2_first_name",
    }

    items_to_update = [item_1_to_update, item_2_to_update]

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))  # noqa
    updated_items: List[Type[UserAggregate]] | None = e_loop.run_until_complete(
        users_service.update_bulk(items=items_to_update, is_return_require=True)
    )
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    assert isinstance(updated_items, list) is True

    updated_items = updated_items or []
    for user_data in updated_items:
        user_data_outdated = [i for i in USERS if i["id"] == user_data.id][0]
        user_data_raw = [i for i in items_to_update if i["id"] == user_data.id][0]

        for key, value in user_data_outdated.items():
            val_updated = getattr(user_data, key)
            if key in user_data_raw:
                value_before = user_data_raw.get(key, None)
            else:
                value_before = user_data_outdated.get(key, None)
            assert val_updated == value_before

    assert count_after == count_before


def test_users_repository_bulk_without_return(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    item_1_to_update = deepcopy(USERS[0])
    item_2_to_update = deepcopy(USERS[1])

    item_1_to_update["first_name"] = "updated_1_first_name"
    item_2_to_update["first_name"] = "updated_2_first_name"

    items_to_update = [item_1_to_update, item_2_to_update]

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))  # noqa
    updated_items: List[Type[UserAggregate]] | None = e_loop.run_until_complete(
        users_service.update_bulk(items=items_to_update, is_return_require=False)
    )
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))
    assert updated_items is None

    for user_data_raw in items_to_update:
        id_ = user_data_raw["id"]
        updated_user: UserAggregate | None = e_loop.run_until_complete(
            users_service.get_first(filter_data={"id": id_})
        )
        for key, value in user_data_raw.items():
            assert getattr(updated_user, key, None) == value
    assert count_after == count_before


USERS_UPDATE_OR_CREATE = [
    USERS[0],
    USERS[1],
    {
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "meta": {
            "first_name": "first_name_n1",
            "last_name": "last_name_n1",
        },
        "birthday": datetime.utcnow(),
        "is_active": True,
        "first_name": "first_name_n1",
        "last_name": "last_name_n1",
        "email": "n1" + generate_str(5) + "@gmail.com",
    },
    {
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "meta": {
            "first_name": "first_name_n2",
            "last_name": "last_name_n2",
        },
        "birthday": datetime.utcnow(),
        "is_active": True,
        "first_name": "first_name_n2",
        "last_name": "last_name_n2",
        "email": "n2" + generate_str(5) + "@gmail.com",
    },
]


@pytest.mark.parametrize("data", USERS_UPDATE_OR_CREATE, scope="function")
def test_update_or_create(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_service = service_container.users_service

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))
    changed_item = e_loop.run_until_complete(
        users_service.update_or_create(filter_data={"email": data["email"]}, data=data, is_return_require=True)
    )
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))
    assert count_after >= count_before
    for key, value in data.items():
        assert getattr(changed_item, key, None) == value


USERS_IS_EXISTS = [
    {"key": "id", "value": USERS[0]["id"], "expected": True},
    {"key": "email", "value": USERS[1]["email"], "expected": True},
    {"key": "email", "value": "not_exists@gmail.com", "expected": False},
]


@pytest.mark.parametrize("data", USERS_IS_EXISTS, scope="function")
def test_users_is_exists(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_service = service_container.users_service

    field = data["key"]
    value = data["value"]
    expected = data["expected"]
    is_exists = e_loop.run_until_complete(users_service.is_exists(filter_data={field: value}))

    assert isinstance(is_exists, bool) is True
    assert is_exists == expected


def test_remove_by_id(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))
    e_loop.run_until_complete(users_service.remove(filter_data={"id": USERS[0]["id"]}))
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))
    assert count_before == count_after + 1

    removed_item = e_loop.run_until_complete(users_service.get_first(filter_data={"id": USERS[0]["id"]}))
    assert removed_item is None


def test_remove_all(e_loop: AbstractEventLoop, users: Any) -> None:
    users_service = service_container.users_service

    count_before = e_loop.run_until_complete(users_service.count(filter_data={}))
    e_loop.run_until_complete(users_service.remove(filter_data={}))
    count_after = e_loop.run_until_complete(users_service.count(filter_data={}))

    assert count_before == len(USERS)
    assert count_after == 0
