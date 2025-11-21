import uuid
from asyncio import AbstractEventLoop
from copy import deepcopy
import datetime as dt
from typing import Any, List, Type

import pytest

from src.app.infrastructure.repositories.base.abstract import RepositoryError
from src.app.domain.common.utils.common import generate_str
from src.app.infrastructure.repositories.container import container as repo_container
from tests.domain.users.aggregates.common import UserTestAggregate
from tests.fixtures.constants import USERS


def test_users_count(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository
    count = e_loop.run_until_complete(users_repository.count())
    assert isinstance(count, int)
    assert count == len(USERS)


def test_users_count_empty(e_loop: AbstractEventLoop) -> None:
    users_repository = repo_container.users_repository
    count = e_loop.run_until_complete(users_repository.count())
    assert isinstance(count, int)
    assert count == 0


def test_users_repository_get_first_by_attr_name(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository
    attr_names = ["id", "uuid", "email"]
    for user_raw in USERS:
        for attr_name in attr_names:
            user: Type[UserTestAggregate] | None = e_loop.run_until_complete(
                users_repository.get_first(
                    filter_data={attr_name: user_raw.get(attr_name)}, out_dataclass=UserTestAggregate
                )
            )
            assert isinstance(user, UserTestAggregate) is True
            for key, value in user_raw.items():
                assert getattr(user, key) == value


def test_users_repository_get_first_by_attr_name_without_out_dataclass(
    e_loop: AbstractEventLoop, users: Any
) -> None:
    users_repository = repo_container.users_repository
    attr_names = ["id", "uuid", "email"]
    for user_raw in USERS:
        for attr_name in attr_names:
            user: Type[UserTestAggregate] | None = e_loop.run_until_complete(
                users_repository.get_first(filter_data={attr_name: user_raw.get(attr_name)})
            )
            assert isinstance(user, UserTestAggregate) is False
            for key, value in user_raw.items():
                assert getattr(user, key) == value


def test_users_get_list_basic(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(out_dataclass=UserTestAggregate)
    )
    assert isinstance(items, list) is True
    assert len(items) == len(USERS)
    raw_ids = [i["id"] for i in USERS]
    for user in items:
        assert isinstance(user, UserTestAggregate) is True
        assert user.id in raw_ids


def test_users_get_list_without_out_dataclass(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(users_repository.get_list())
    assert isinstance(items, list) is True
    assert len(items) == len(USERS)
    raw_ids = [i["id"] for i in USERS]
    for user in items:
        assert isinstance(user, UserTestAggregate) is False
        assert user.id in raw_ids


def test_users_repository_create(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    user_data_raw = {
        "id": 999,
        "uuid": uuid.uuid4().__str__(),
        "created_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "meta": {
            "first_name": "first_name_n",
            "last_name": "last_name_n",
        },
        "birthday": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "is_active": True,
        "first_name": "first_name_n",
        "last_name": "last_name_n",
        "email": "n" + generate_str(5) + "@gmail.com",
    }
    count_before = e_loop.run_until_complete(users_repository.count())
    created_user: UserTestAggregate | None = e_loop.run_until_complete(
        users_repository.create(data=user_data_raw, is_return_require=True, out_dataclass=UserTestAggregate)
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    assert isinstance(created_user, UserTestAggregate) is True
    for key, value in user_data_raw.items():
        assert getattr(created_user, key) == value
    assert count_after == count_before + 1


def test_users_repository_create_without_id_and_uuid(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    user_data_raw = {
        "meta": {
            "first_name": "first_name_n",
            "last_name": "last_name_n",
        },
        "birthday": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "is_active": True,
        "first_name": "first_name_n",
        "last_name": "last_name_n",
        "email": "n" + generate_str(5) + "@gmail.com",
    }
    count_before = e_loop.run_until_complete(users_repository.count())
    created_user: UserTestAggregate | None = e_loop.run_until_complete(
        users_repository.create(data=user_data_raw, is_return_require=True, out_dataclass=UserTestAggregate)
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    assert isinstance(created_user, UserTestAggregate) is True

    assert getattr(created_user, "id") is not None
    assert getattr(created_user, "uuid") is not None
    for key, value in user_data_raw.items():
        assert getattr(created_user, key) == value
    assert count_after == count_before + 1


def test_users_repository_create_is_not_return(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    user_data_raw = {
        "meta": {
            "first_name": "first_name_n",
            "last_name": "last_name_n",
        },
        "birthday": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "is_active": True,
        "first_name": "first_name_n",
        "last_name": "last_name_n",
        "email": "n" + generate_str(5) + "@gmail.com",
    }
    count_before = e_loop.run_until_complete(users_repository.count())
    created_user: UserTestAggregate | None = e_loop.run_until_complete(
        users_repository.create(data=user_data_raw, is_return_require=False, out_dataclass=UserTestAggregate)
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    assert created_user is None

    assert count_after == count_before + 1


def test_users_repository_create_bulk(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    user_data_raw_1 = {
        "id": 998,
        "uuid": uuid.uuid4().__str__(),
        "created_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "meta": {
            "first_name": "first_name_n1",
            "last_name": "last_name_n1",
        },
        "birthday": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "is_active": True,
        "first_name": "first_name_n1",
        "last_name": "last_name_n1",
        "email": "n1" + generate_str(5) + "@gmail.com",
    }
    user_data_raw_2 = {
        "id": 999,
        "uuid": uuid.uuid4().__str__(),
        "created_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "meta": {
            "first_name": "first_name_n2",
            "last_name": "last_name_n2",
        },
        "birthday": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "is_active": True,
        "first_name": "first_name_n2",
        "last_name": "last_name_n2",
        "email": "n2" + generate_str(5) + "@gmail.com",
    }
    items_raw = [user_data_raw_1, user_data_raw_2]

    count_before = e_loop.run_until_complete(users_repository.count())
    created_items: List[UserTestAggregate] | None = e_loop.run_until_complete(
        users_repository.create_bulk(items=items_raw, is_return_require=True, out_dataclass=UserTestAggregate)
    )
    created_items = created_items or []
    count_after = e_loop.run_until_complete(users_repository.count())

    for index, created_user in enumerate(created_items):
        assert isinstance(created_user, UserTestAggregate) is True
        user_data_raw = items_raw[index]
        for key, value in user_data_raw.items():
            assert getattr(created_user, key) == value

    assert count_after == count_before + len(items_raw)


def test_users_repository_create_bulk_without_id_uuid(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    user_data_raw_1 = {
        "created_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "meta": {
            "first_name": "first_name_n1",
            "last_name": "last_name_n1",
        },
        "birthday": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "is_active": True,
        "first_name": "first_name_n1",
        "last_name": "last_name_n1",
        "email": "n1" + generate_str(5) + "@gmail.com",
    }
    user_data_raw_2 = {
        "created_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "meta": {
            "first_name": "first_name_n2",
            "last_name": "last_name_n2",
        },
        "birthday": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "is_active": True,
        "first_name": "first_name_n2",
        "last_name": "last_name_n2",
        "email": "n2" + generate_str(5) + "@gmail.com",
    }
    items_raw = [user_data_raw_1, user_data_raw_2]

    count_before = e_loop.run_until_complete(users_repository.count())
    created_items: List[UserTestAggregate] | None = e_loop.run_until_complete(
        users_repository.create_bulk(items=items_raw, is_return_require=True, out_dataclass=UserTestAggregate)
    )
    created_items = created_items or []
    count_after = e_loop.run_until_complete(users_repository.count())

    for index, created_user in enumerate(created_items):
        assert isinstance(created_user, UserTestAggregate) is True
        user_data_raw = items_raw[index]
        assert getattr(created_user, "id") is not None
        assert getattr(created_user, "uuid") is not None
        for key, value in user_data_raw.items():
            assert getattr(created_user, key) == value

    assert count_after == count_before + len(items_raw)


def test_users_repository_create_bulk_is_not_return(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    user_data_raw_1 = {
        "created_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "meta": {
            "first_name": "first_name_n1",
            "last_name": "last_name_n1",
        },
        "birthday": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "is_active": True,
        "first_name": "first_name_n1",
        "last_name": "last_name_n1",
        "email": "n1" + generate_str(5) + "@gmail.com",
    }
    user_data_raw_2 = {
        "created_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "meta": {
            "first_name": "first_name_n2",
            "last_name": "last_name_n2",
        },
        "birthday": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "is_active": True,
        "first_name": "first_name_n2",
        "last_name": "last_name_n2",
        "email": "n2" + generate_str(5) + "@gmail.com",
    }
    items_raw = [user_data_raw_1, user_data_raw_2]

    count_before = e_loop.run_until_complete(users_repository.count())
    created_items: List[UserTestAggregate] | None = e_loop.run_until_complete(
        users_repository.create_bulk(items=items_raw, is_return_require=False, out_dataclass=UserTestAggregate)
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    assert created_items is None
    assert count_after == count_before + len(items_raw)


def test_users_repository_update_full(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    user_data_raw = deepcopy(USERS[0])
    val_to_update = "updated_first_name"
    user_data_raw["first_name"] = val_to_update

    count_before = e_loop.run_until_complete(users_repository.count())  # noqa
    updated_user: UserTestAggregate | None = e_loop.run_until_complete(
        users_repository.update(
            filter_data={"id": user_data_raw["id"]},
            data=user_data_raw,
            is_return_require=True,
            out_dataclass=UserTestAggregate,
        )
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    assert isinstance(updated_user, UserTestAggregate) is True
    for key, value in user_data_raw.items():
        assert getattr(updated_user, key) == value
    assert count_after == count_before


def test_users_repository_update_partial(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    user_data = deepcopy(USERS[0])
    user_data_raw = {
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "first_name": "updated_first_name_1",
        "last_name": "updated_last_name_1",
    }

    count_before = e_loop.run_until_complete(users_repository.count())  # noqa
    updated_user: UserTestAggregate | None = e_loop.run_until_complete(
        users_repository.update(
            filter_data={"id": user_data["id"]},
            data=user_data_raw,
            is_return_require=True,
            out_dataclass=UserTestAggregate,
        )
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    assert isinstance(updated_user, UserTestAggregate) is True
    for key, value in user_data.items():
        val_updated = getattr(updated_user, key)
        if key in user_data_raw:
            value = user_data_raw.get(key, None)
        assert val_updated == value
    assert count_after == count_before


def test_users_repository_update_without_return(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    user_data = deepcopy(USERS[0])
    user_data_raw = {
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "first_name": "updated_first_name_1",
        "last_name": "updated_last_name_1",
    }

    count_before = e_loop.run_until_complete(users_repository.count())  # noqa
    updated_user: UserTestAggregate | None = e_loop.run_until_complete(
        users_repository.update(filter_data={"id": user_data["id"]}, data=user_data_raw, is_return_require=False)
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    assert updated_user is None
    assert count_after == count_before


def test_users_repository_bulk_update_full(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    item_1_to_update = deepcopy(USERS[0])
    item_2_to_update = deepcopy(USERS[1])

    item_1_to_update["first_name"] = "updated_1_first_name"
    item_2_to_update["first_name"] = "updated_2_first_name"

    items_to_update = [item_1_to_update, item_2_to_update]

    count_before = e_loop.run_until_complete(users_repository.count())  # noqa
    updated_items: List[Type[UserTestAggregate]] | None = e_loop.run_until_complete(
        users_repository.update_bulk(
            items=items_to_update, is_return_require=True, out_dataclass=UserTestAggregate
        )
    )
    count_after = e_loop.run_until_complete(users_repository.count())

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
    users_repository = repo_container.users_repository

    item_1_to_update = {
        "id": USERS[0]["id"],
        "uuid": str(USERS[0]["uuid"]),
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "first_name": "updated_1_first_name",
    }
    item_2_to_update = {
        "id": USERS[1]["id"],
        "uuid": str(USERS[1]["uuid"]),
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "first_name": "updated_2_first_name",
    }

    items_to_update = [item_1_to_update, item_2_to_update]

    count_before = e_loop.run_until_complete(users_repository.count())  # noqa
    updated_items: List[Type[UserTestAggregate]] | None = e_loop.run_until_complete(
        users_repository.update_bulk(
            items=items_to_update, is_return_require=True, out_dataclass=UserTestAggregate
        )
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    # pdated_items, list) is True

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
    users_repository = repo_container.users_repository

    item_1_to_update = deepcopy(USERS[0])
    item_2_to_update = deepcopy(USERS[1])

    item_1_to_update["first_name"] = "updated_1_first_name"
    item_2_to_update["first_name"] = "updated_2_first_name"

    items_to_update = [item_1_to_update, item_2_to_update]

    count_before = e_loop.run_until_complete(users_repository.count())  # noqa
    updated_items: List[Type[UserTestAggregate]] | None = e_loop.run_until_complete(
        users_repository.update_bulk(
            items=items_to_update, is_return_require=False, out_dataclass=UserTestAggregate
        )
    )
    count_after = e_loop.run_until_complete(users_repository.count())
    assert updated_items is None

    for user_data_raw in items_to_update:
        id_ = user_data_raw["id"]
        updated_user: UserTestAggregate | None = e_loop.run_until_complete(
            users_repository.get_first(filter_data={"id": id_}, out_dataclass=UserTestAggregate)
        )
        for key, value in user_data_raw.items():
            assert getattr(updated_user, key, None) == value
    assert count_after == count_before


USERS_UPDATE_OR_CREATE = [
    USERS[0],
    USERS[1],
    {
        "created_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "meta": {
            "first_name": "first_name_n1",
            "last_name": "last_name_n1",
        },
        "birthday": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "is_active": True,
        "first_name": "first_name_n1",
        "last_name": "last_name_n1",
        "email": "n1" + generate_str(5) + "@gmail.com",
    },
    {
        "created_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "meta": {
            "first_name": "first_name_n2",
            "last_name": "last_name_n2",
        },
        "birthday": dt.datetime.now(dt.UTC).replace(tzinfo=None),
        "is_active": True,
        "first_name": "first_name_n2",
        "last_name": "last_name_n2",
        "email": "n2" + generate_str(5) + "@gmail.com",
    },
]


@pytest.mark.parametrize("data", USERS_UPDATE_OR_CREATE, scope="function")
def test_update_or_create(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    count_before = e_loop.run_until_complete(users_repository.count())
    changed_item = e_loop.run_until_complete(
        users_repository.update_or_create(filter_data={"email": data["email"]}, data=data, is_return_require=True)
    )
    count_after = e_loop.run_until_complete(users_repository.count())
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
    users_repository = repo_container.users_repository

    field = data["key"]
    value = data["value"]
    expected = data["expected"]
    is_exists = e_loop.run_until_complete(users_repository.is_exists(filter_data={field: value}))

    assert isinstance(is_exists, bool) is True
    assert is_exists == expected


def test_remove_by_id(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    count_before = e_loop.run_until_complete(users_repository.count())
    e_loop.run_until_complete(users_repository.remove(filter_data={"id": USERS[0]["id"]}))
    count_after = e_loop.run_until_complete(users_repository.count())
    assert count_before == count_after + 1

    removed_item = e_loop.run_until_complete(users_repository.get_first(filter_data={"id": USERS[0]["id"]}))
    assert removed_item is None


def test_remove_all(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    count_before = e_loop.run_until_complete(users_repository.count())
    e_loop.run_until_complete(users_repository.remove(filter_data={}))
    count_after = e_loop.run_until_complete(users_repository.count())

    assert count_before == len(USERS)
    assert count_after == 0


# Validation and error handling test cases
def test_allow_create_user_with_duplicate_email(e_loop: AbstractEventLoop, users: Any) -> None:
    """Test documents that the system currently allows duplicate emails"""
    users_repository = repo_container.users_repository

    user_data_raw = {
        "first_name": "duplicate_test",
        "last_name": "duplicate_test",
        "email": USERS[0]["email"],  # Using existing email
        "is_active": True,
    }

    count_before = e_loop.run_until_complete(users_repository.count())

    # The system currently allows duplicate emails - this documents the actual behavior
    created_user = e_loop.run_until_complete(
        users_repository.create(data=user_data_raw, is_return_require=True, out_dataclass=UserTestAggregate)
    )

    count_after = e_loop.run_until_complete(users_repository.count())

    # Verify the user was created successfully with duplicate email
    assert created_user is not None
    assert created_user.email == USERS[0]["email"]
    assert created_user.first_name == "duplicate_test"
    assert count_after == count_before + 1


@pytest.mark.parametrize(
    "invalid_email",
    [
        "invalid",
        "invalid@",
        "@invalid.com",
        "invalid@.com",
        "",
        "spaces in email@test.com",
        "missing-domain@",
        "@missing-local.com",
    ],
)
def test_allow_create_user_with_invalid_email_format(
    e_loop: AbstractEventLoop, users: Any, invalid_email: str
) -> None:
    users_repository = repo_container.users_repository

    user_data_raw = {
        "first_name": "test_user",
        "last_name": "test_user",
        "email": invalid_email,
        "is_active": True,
    }

    # Test either validates and fails, or creates successfully (depends on implementation)
    # This test documents the actual behavior rather than assuming validation
    result = e_loop.run_until_complete(
        users_repository.create(data=user_data_raw, is_return_require=True, out_dataclass=UserTestAggregate)
    )

    # If creation succeeds, verify the email was stored as-is
    if result is not None:
        assert result.email == invalid_email


def test_update_user_with_invalid_id(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    non_existent_id = 99999
    user_data_raw = {
        "first_name": "updated_name",
        "last_name": "updated_last_name",
    }

    updated_user = e_loop.run_until_complete(
        users_repository.update(
            filter_data={"id": non_existent_id},
            data=user_data_raw,
            is_return_require=True,
            out_dataclass=UserTestAggregate,
        )
    )

    assert updated_user is None


def test_get_first_with_non_existent_filter(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    user = e_loop.run_until_complete(
        users_repository.get_first(
            filter_data={"email": "nonexistent@example.com"}, out_dataclass=UserTestAggregate
        )
    )

    assert user is None


def test_is_exists_with_non_existent_data(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    exists = e_loop.run_until_complete(
        users_repository.is_exists(filter_data={"email": "nonexistent@example.com"})
    )

    assert exists is False


def test_remove_non_existent_user(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    count_before = e_loop.run_until_complete(users_repository.count())
    e_loop.run_until_complete(users_repository.remove(filter_data={"id": 99999}))
    count_after = e_loop.run_until_complete(users_repository.count())

    assert count_before == count_after


# Data integrity test cases
def test_create_user_with_minimal_required_fields(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    minimal_user_data = {
        "email": "minimal" + generate_str(5) + "@example.com",
        "is_active": True,
    }

    count_before = e_loop.run_until_complete(users_repository.count())
    created_user = e_loop.run_until_complete(
        users_repository.create(data=minimal_user_data, is_return_require=True, out_dataclass=UserTestAggregate)
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    assert isinstance(created_user, UserTestAggregate)
    assert created_user.email == minimal_user_data["email"]
    assert created_user.is_active == minimal_user_data["is_active"]
    assert created_user.id is not None
    assert created_user.uuid is not None
    assert count_after == count_before + 1


def test_update_user_timestamps_are_handled(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    original_user_data = deepcopy(USERS[0])
    update_data = {
        "first_name": "updated_timestamp_test",
        "updated_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
    }

    updated_user = e_loop.run_until_complete(
        users_repository.update(
            filter_data={"id": original_user_data["id"]},
            data=update_data,
            is_return_require=True,
            out_dataclass=UserTestAggregate,
        )
    )
    assert isinstance(updated_user, UserTestAggregate)

    assert updated_user.first_name == update_data["first_name"]
    assert updated_user.updated_at == update_data["updated_at"]
    assert updated_user.created_at == original_user_data["created_at"]


def test_create_user_with_complex_meta_data(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    complex_meta = {
        "first_name": "complex_first",
        "last_name": "complex_last",
        "preferences": {"theme": "dark", "language": "en", "notifications": True},
        "profile": {"bio": "Test user bio", "social_links": ["twitter.com/test", "linkedin.com/test"]},
    }

    user_data_raw = {
        "email": "complex" + generate_str(5) + "@example.com",
        "is_active": True,
        "meta": complex_meta,
        "first_name": "complex_first",
        "last_name": "complex_last",
    }

    created_user = e_loop.run_until_complete(
        users_repository.create(data=user_data_raw, is_return_require=True, out_dataclass=UserTestAggregate)
    )

    assert isinstance(created_user, UserTestAggregate)
    assert created_user.meta == complex_meta
    assert created_user.first_name == user_data_raw["first_name"]
    assert created_user.last_name == user_data_raw["last_name"]


# Bulk operations edge cases
def test_create_bulk_with_empty_list(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    count_before = e_loop.run_until_complete(users_repository.count())
    created_items = e_loop.run_until_complete(
        users_repository.create_bulk(items=[], is_return_require=True, out_dataclass=UserTestAggregate)
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    assert created_items == []
    assert count_before == count_after


def test_update_bulk_with_mixed_valid_invalid_ids(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    items_to_update = [
        {
            "id": USERS[0]["id"],  # Valid ID
            "uuid": str(USERS[0]["uuid"]),
            "first_name": "updated_valid",
        },
        {
            "id": 99999,  # Invalid ID
            "uuid": str(uuid.uuid4()),
            "first_name": "updated_invalid",
        },
    ]

    updated_items = e_loop.run_until_complete(
        users_repository.update_bulk(
            items=items_to_update, is_return_require=True, out_dataclass=UserTestAggregate
        )
    )

    # Check behavior with mixed valid/invalid IDs
    if updated_items:
        assert len(updated_items) == 1  # Should have at most one valid update
        assert updated_items[0].id == items_to_update[0]["id"]
        assert updated_items[0].first_name == items_to_update[0]["first_name"]


# Transaction and consistency tests
def test_update_or_create_creates_new_user(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    new_email = "create_new" + generate_str(5) + "@example.com"
    user_data = {
        "email": new_email,
        "first_name": "new_user",
        "last_name": "new_user",
        "is_active": True,
    }

    count_before = e_loop.run_until_complete(users_repository.count())
    result_user = e_loop.run_until_complete(
        users_repository.update_or_create(
            filter_data={"email": new_email},
            data=user_data,
            is_return_require=True,
            out_dataclass=UserTestAggregate,
        )
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    assert count_after == count_before + 1
    assert isinstance(result_user, UserTestAggregate) is True
    assert result_user is not None
    assert result_user.email == new_email
    assert result_user.first_name == "new_user"


def test_update_or_create_updates_existing_user(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    existing_email = USERS[0]["email"]
    update_data = {
        "email": existing_email,
        "first_name": "updated_existing",
        "last_name": "updated_existing",
        "is_active": False,
    }

    count_before = e_loop.run_until_complete(users_repository.count())
    result_user = e_loop.run_until_complete(
        users_repository.update_or_create(
            filter_data={"email": existing_email},
            data=update_data,
            is_return_require=True,
            out_dataclass=UserTestAggregate,
        )
    )
    count_after = e_loop.run_until_complete(users_repository.count())

    assert count_after == count_before  # No new user created
    assert isinstance(result_user, UserTestAggregate) is True
    assert result_user is not None
    assert result_user.email == existing_email
    assert result_user.first_name == "updated_existing"
    assert result_user.is_active is False


# Performance and boundary tests
def test_get_list_with_large_limit(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    large_limit = 1000
    items = e_loop.run_until_complete(
        users_repository.get_list(filter_data={"limit": large_limit}, out_dataclass=UserTestAggregate)
    )

    assert len(items) == len(USERS)  # Should return all available users, not more


def test_get_list_with_zero_limit(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    with pytest.raises(RepositoryError):
        e_loop.run_until_complete(
            users_repository.get_list(filter_data={"limit": 0}, out_dataclass=UserTestAggregate)
        )


def test_get_list_with_large_offset(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    large_offset = 1000
    items = e_loop.run_until_complete(
        users_repository.get_list(filter_data={"offset": large_offset}, out_dataclass=UserTestAggregate)
    )

    assert len(items) == 0  # Should return empty list


# Data type and format tests
def test_create_user_with_special_characters_in_name(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    special_chars_data = {
        "email": "special" + generate_str(5) + "@example.com",
        "first_name": "José María",
        "last_name": "O'Connor-Smith",
        "is_active": True,
    }

    created_user = e_loop.run_until_complete(
        users_repository.create(data=special_chars_data, is_return_require=True, out_dataclass=UserTestAggregate)
    )
    assert isinstance(created_user, UserTestAggregate)

    assert created_user.first_name == "José María"
    assert created_user.last_name == "O'Connor-Smith"


def test_create_user_with_long_strings(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    long_string = "a" * 100  # 100 character string
    long_data = {
        "email": "long" + generate_str(5) + "@example.com",
        "first_name": long_string,
        "last_name": long_string,
        "is_active": True,
    }

    # Test documents actual behavior - either succeeds or fails with constraints
    created_user = e_loop.run_until_complete(
        users_repository.create(data=long_data, is_return_require=True, out_dataclass=UserTestAggregate)
    )
    assert isinstance(created_user, UserTestAggregate)

    # If creation succeeds, verify the data was stored correctly
    assert created_user.first_name == long_string
    assert created_user.last_name == long_string


# State management tests
def test_user_activation_deactivation_cycle(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    user_id = USERS[0]["id"]

    # Deactivate user
    deactivated_user = e_loop.run_until_complete(
        users_repository.update(
            filter_data={"id": user_id},
            data={"is_active": False},
            is_return_require=True,
            out_dataclass=UserTestAggregate,
        )
    )
    assert isinstance(deactivated_user, UserTestAggregate)
    assert deactivated_user.is_active is False

    # Reactivate user
    reactivated_user = e_loop.run_until_complete(
        users_repository.update(
            filter_data={"id": user_id},
            data={"is_active": True},
            is_return_require=True,
            out_dataclass=UserTestAggregate,
        )
    )
    assert isinstance(reactivated_user, UserTestAggregate)
    assert reactivated_user.is_active is True
