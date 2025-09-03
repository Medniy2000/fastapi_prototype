from asyncio import AbstractEventLoop
from typing import Any, List, Type

import pytest


from src.app.infrastructure.repositories.container import container as repo_container
from tests.domain.users.aggregates.common import UserTestAggregate
from tests.fixtures.constants import USERS


def test_users_get_list_limit_offset_case_1(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    count = len(USERS)
    offset = count - 1
    limit = 10
    expected_count = 1  # noqa

    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={"limit": limit, "offset": offset}, out_dataclass=UserTestAggregate),
    )
    assert isinstance(items, list) is True
    assert len(items) == expected_count

    raw_ids = [i["id"] for i in USERS]
    for user in items:
        assert isinstance(user, UserTestAggregate) is True
        assert user.id in raw_ids


def test_users_get_list_limit_offset_case_2(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository

    count = len(USERS)
    offset = count - 2
    limit = 10
    expected_count = 2

    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(  # noqa
        users_repository.get_list(filter_data={"limit": limit, "offset": offset}, out_dataclass=UserTestAggregate)
    )
    assert isinstance(items, list) is True
    assert len(items) == expected_count

    raw_ids = [i["id"] for i in USERS]
    for user in items:
        assert isinstance(user, UserTestAggregate) is True
        assert user.id in raw_ids


def test_users_get_list_limit_offset_case_3(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository
    count = len(USERS)
    offset = count - 2
    limit = 1
    expected_count = 1  # noqa
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={"limit": limit, "offset": offset}, out_dataclass=UserTestAggregate)
    )
    assert isinstance(items, list) is True
    assert len(items) == expected_count

    raw_ids = [i["id"] for i in USERS]
    for user in items:
        assert isinstance(user, UserTestAggregate) is True
        assert user.id in raw_ids


def test_users_get_list_limit_offset_case_4(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository
    count = len(USERS)
    offset = 1
    expected_count = count - offset
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={"offset": offset}, out_dataclass=UserTestAggregate)
    )
    assert isinstance(items, list) is True
    assert len(items) == expected_count

    raw_ids = [i["id"] for i in USERS]
    for user in items:
        assert isinstance(user, UserTestAggregate) is True
        assert user.id in raw_ids


def test_users_get_list_order_by_id_asc(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository
    USERS_RAW = sorted(USERS, key=lambda i: i["id"])
    count = len(USERS_RAW)

    items: List[UserTestAggregate] = e_loop.run_until_complete(
        users_repository.get_list(order_data=("id",), out_dataclass=UserTestAggregate)
    )
    assert isinstance(items, list) is True
    assert len(items) == count

    for index, user in enumerate(items):
        assert isinstance(user, UserTestAggregate) is True
        assert user.id == USERS_RAW[index]["id"]


def test_users_get_list_order_by_id_desc(e_loop: AbstractEventLoop, users: Any) -> None:
    users_repository = repo_container.users_repository
    USERS_RAW = sorted(USERS, key=lambda i: i["id"], reverse=True)
    count = len(USERS_RAW)

    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(order_data=("-id",), out_dataclass=UserTestAggregate)
    )
    assert isinstance(items, list) is True
    assert len(items) == count

    for index, user in enumerate(items):
        assert isinstance(user, UserTestAggregate) is True
        assert user.id == USERS_RAW[index]["id"]


USERS_IN_LOOKUP = [
    {"key": "id", "value": [USERS[0]["id"], USERS[2]["id"], USERS[3]["id"]]},
    {"key": "first_name", "value": [USERS[1]["first_name"], USERS[2]["first_name"], USERS[3]["first_name"]]},
    {"key": "email", "value": [USERS[1]["email"], USERS[2]["email"], USERS[3]["email"]]},
]


@pytest.mark.parametrize("data", USERS_IN_LOOKUP, scope="function")
def test_users_get_list_in_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__in"
    expected_values = data["value"]
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=UserTestAggregate)
    )

    assert isinstance(items, list) is True
    assert len(items) == len(expected_values)

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert value in expected_values


USERS_GT_LOOKUP = [
    {"key": "id", "value": 1},
    {"key": "id", "value": 5},
]


@pytest.mark.parametrize("data", USERS_GT_LOOKUP, scope="function")
def test_users_get_list_gt_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__gt"
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=UserTestAggregate)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert value > data["value"]


USERS_GTE_LOOKUP = [
    {"key": "id", "value": 3},
    {"key": "id", "value": 4},
    {"key": "id", "value": 5},
]


@pytest.mark.parametrize("data", USERS_GTE_LOOKUP, scope="function")
def test_users_get_list_gte_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__gt"
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=UserTestAggregate)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert value >= data["value"]


USERS_LT_LOOKUP = [
    {"key": "id", "value": 1},
    {"key": "id", "value": 3},
    {"key": "id", "value": 4},
]


@pytest.mark.parametrize("data", USERS_LT_LOOKUP, scope="function")
def test_users_get_list_lt_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__lt"
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=UserTestAggregate)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert value < data["value"]


USERS_LTE_LOOKUP = [
    {"key": "id", "value": 1},
    {"key": "id", "value": 3},
    {"key": "id", "value": 4},
]


@pytest.mark.parametrize("data", USERS_LTE_LOOKUP, scope="function")
def test_users_get_list_lte_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__lte"
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=UserTestAggregate)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert value <= data["value"]


USERS_E_LOOKUP = [
    {"key": "id", "value": USERS[0]["id"]},
    {"key": "first_name", "value": USERS[0]["first_name"]},
    {"key": "email", "value": USERS[0]["email"]},
    {"key": "birthday", "value": USERS[0]["birthday"]},
]


@pytest.mark.parametrize("data", USERS_E_LOOKUP, scope="function")
def test_users_get_list_e_lookup_case_1(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__e"
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=UserTestAggregate)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert value == data["value"]


@pytest.mark.parametrize("data", USERS_E_LOOKUP, scope="function")
def test_users_get_list_e_lookup_case_2(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = field
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=UserTestAggregate)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert value == data["value"]


USERS_NE_LOOKUP = [
    {"key": "id", "value": USERS[0]["id"]},
    {"key": "first_name", "value": USERS[1]["first_name"]},
    {"key": "email", "value": USERS[2]["email"]},
    {"key": "birthday", "value": USERS[3]["birthday"]},
]


@pytest.mark.parametrize("data", USERS_NE_LOOKUP, scope="function")
def test_users_get_list_ne_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__ne"
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=UserTestAggregate)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert value != data["value"]


USERS_NOT_IN_LOOKUP = [
    {"key": "id", "value": [USERS[0]["id"]]},
    {"key": "first_name", "value": [USERS[1]["first_name"], USERS[2]["first_name"]]},
    {"key": "email", "value": [USERS[2]["email"], USERS[3]["email"]]},
    {"key": "birthday", "value": [USERS[3]["birthday"]]},
]


@pytest.mark.parametrize("data", USERS_NOT_IN_LOOKUP, scope="function")
def test_users_get_list_not_in_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__not_in"
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=UserTestAggregate)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert value not in data["value"]


USERS_LIKE_LOOKUP = [
    {"key": "id", "value": USERS[0]["id"]},
    {"key": "first_name", "value": USERS[1]["first_name"]},
    {
        "key": "email",
        "value": USERS[2]["email"],
    },
    {
        "key": "email",
        "value": "gmail",
    },
    {"key": "birthday", "value": USERS[3]["birthday"]},
]


@pytest.mark.parametrize("data", USERS_LIKE_LOOKUP, scope="function")
def test_users_get_list_like_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__like"
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=UserTestAggregate)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert str(data["value"]) in str(value)


USERS_NOT_LIKE_ALL_LOOKUP = [
    {"key": "id", "value": [USERS[0]["id"], USERS[1]["id"]]},
    {"key": "first_name", "value": ["name_1", "name_2"]},
    {
        "key": "email",
        "value": ["1_", "3_"],
    },
]


@pytest.mark.parametrize("data", USERS_NOT_LIKE_ALL_LOOKUP, scope="function")
def test_users_get_list_not_like_all_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__not_like_all"
    items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=UserTestAggregate)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert str(data["value"]) not in str(value)


USERS_JSONB_LIKE_LOOKUP = [
    {"key": "first_name", "value": [USERS[0]["id"], USERS[1]["id"]]},
    {"key": "last_name", "value": ["name_1", "name_2"]},
    {"key": "last_name", "value": ["last_name_1", "last_name_2"]},
    {"key": "first_name", "value": ["first_name_1", "first_name_1"]},
]


@pytest.mark.parametrize("data", USERS_JSONB_LIKE_LOOKUP, scope="function")
def test_users_get_list_jsonb_like_lookup_case_1(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__jsonb_like"
    for value in data["value"]:
        items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
            users_repository.get_list(
                filter_data={lookup: value},
                out_dataclass=UserTestAggregate,
            )
        )

        assert isinstance(items, list) is True

        for index, user in enumerate(items):
            data = getattr(user, "meta", {})
            data_value = data.get(field)
            assert str(value) in str(data_value)


@pytest.mark.parametrize("data", USERS_JSONB_LIKE_LOOKUP, scope="function")
def test_users_get_list_jsonb_like_lookup_case_2(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"meta__{field}__jsonb_like"
    for value in data["value"]:
        items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
            users_repository.get_list(filter_data={lookup: value}, out_dataclass=UserTestAggregate)
        )

        assert isinstance(items, list) is True

        for index, user in enumerate(items):
            data = getattr(user, "meta", {})
            data_value = data.get(field)
            assert str(value) in str(data_value)


USERS_JSONB_NOT_LIKE_LOOKUP = [
    {"key": "first_name", "value": [USERS[0]["id"], USERS[1]["id"]]},
    {"key": "last_name", "value": ["name_1", "name_2"]},
    {"key": "last_name", "value": ["last_name_1", "last_name_2"]},
    {"key": "first_name", "value": ["first_name_2", "first_name_3"]},
]


@pytest.mark.parametrize("data", USERS_JSONB_NOT_LIKE_LOOKUP, scope="function")
def test_users_get_list_jsonb_not_like_lookup_case_1(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"{field}__jsonb_not_like"
    for value in data["value"]:
        items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
            users_repository.get_list(filter_data={lookup: value}, out_dataclass=UserTestAggregate)
        )

        assert isinstance(items, list) is True

        for index, user in enumerate(items):
            data = getattr(user, "meta", {})
            data_value = data.get(field)

            assert str(value) not in str(data_value)


@pytest.mark.parametrize("data", USERS_JSONB_NOT_LIKE_LOOKUP, scope="function")
def test_users_get_list_jsonb_not_like_lookup_case_2(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repo_container.users_repository

    field = data["key"]
    lookup = f"meta__{field}__jsonb_not_like"
    for value in data["value"]:
        items: List[Type[UserTestAggregate]] = e_loop.run_until_complete(
            users_repository.get_list(filter_data={lookup: value}, out_dataclass=UserTestAggregate)
        )

        assert isinstance(items, list) is True

        for index, user in enumerate(items):
            data = getattr(user, "meta", {})
            data_value = data.get(field)
            assert str(value) not in str(data_value)
