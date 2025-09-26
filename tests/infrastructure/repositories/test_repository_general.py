from asyncio import AbstractEventLoop
from typing import Any, List, Type

import pytest


from src.app.infrastructure.repositories.container import container as repo_container
from tests.domain.users.aggregates.common import UserTestAggregate
from tests.fixtures.constants import USERS


repository = repo_container.users_repository
out_dataclass = UserTestAggregate


def test_get_list_limit_offset_case_1(e_loop: AbstractEventLoop, users: Any) -> None:
    """Test pagination with limit larger than remaining items"""

    total_users = len(USERS)
    offset = total_users - 1
    limit = 10
    expected_count = 1

    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={"limit": limit, "offset": offset}, out_dataclass=out_dataclass),
    )

    assert isinstance(items, list)
    assert len(items) == expected_count

    # Verify returned item is valid
    expected_ids = {user["id"] for user in USERS}
    for user in items:
        assert isinstance(user, out_dataclass)
        assert user.id in expected_ids


def test_get_list_limit_offset_case_2(e_loop: AbstractEventLoop, users: Any) -> None:
    """Test pagination with offset near end of dataset"""

    total_users = len(USERS)
    offset = total_users - 2
    limit = 10
    expected_count = 2

    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={"limit": limit, "offset": offset}, out_dataclass=out_dataclass)
    )

    assert isinstance(items, list)
    assert len(items) == expected_count

    expected_ids = {user["id"] for user in USERS}
    for user in items:
        assert isinstance(user, out_dataclass)
        assert user.id in expected_ids


def test_get_list_limit_offset_case_3(e_loop: AbstractEventLoop, users: Any) -> None:
    """Test pagination with small limit and large offset"""

    total_users = len(USERS)
    offset = total_users - 2
    limit = 1
    expected_count = 1

    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={"limit": limit, "offset": offset}, out_dataclass=out_dataclass)
    )

    assert isinstance(items, list)
    assert len(items) == expected_count

    expected_ids = {user["id"] for user in USERS}
    for user in items:
        assert isinstance(user, out_dataclass)
        assert user.id in expected_ids


def test_get_list_with_offset_only(e_loop: AbstractEventLoop, users: Any) -> None:
    """Test pagination with offset but no limit"""

    total_users = len(USERS)
    offset = 1
    expected_count = total_users - offset

    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={"offset": offset}, out_dataclass=out_dataclass)
    )

    assert isinstance(items, list)
    assert len(items) == expected_count

    expected_ids = {user["id"] for user in USERS}
    for user in items:
        assert isinstance(user, out_dataclass)
        assert user.id in expected_ids


def test_get_list_order_by_id_asc(e_loop: AbstractEventLoop, users: Any) -> None:
    """Test ordering users by ID in ascending order"""

    users_sorted = sorted(USERS, key=lambda i: i["id"])
    expected_count = len(users_sorted)

    items: List[out_dataclass] = e_loop.run_until_complete(
        repository.get_list(order_data=("id",), out_dataclass=out_dataclass)
    )

    assert isinstance(items, list)
    assert len(items) == expected_count

    # Verify ordering is correct
    for index, user in enumerate(items):
        assert isinstance(user, out_dataclass)
        assert user.id == users_sorted[index]["id"]

    # Verify items are in ascending order
    user_ids = [user.id for user in items]
    assert user_ids == sorted(user_ids)


def test_get_list_order_by_id_desc(e_loop: AbstractEventLoop, users: Any) -> None:
    """Test ordering users by ID in descending order"""

    users_sorted = sorted(USERS, key=lambda i: i["id"], reverse=True)
    expected_count = len(users_sorted)

    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(order_data=("-id",), out_dataclass=out_dataclass)
    )

    assert isinstance(items, list)
    assert len(items) == expected_count

    # Verify ordering is correct
    for index, user in enumerate(items):
        assert isinstance(user, out_dataclass)
        assert user.id == users_sorted[index]["id"]

    # Verify items are in descending order
    user_ids = [user.id for user in items]
    assert user_ids == sorted(user_ids, reverse=True)


USERS_IN_LOOKUP = [
    {"key": "id", "value": [USERS[0]["id"], USERS[2]["id"], USERS[3]["id"]]},
    {"key": "first_name", "value": [USERS[1]["first_name"], USERS[2]["first_name"], USERS[3]["first_name"]]},
    {"key": "email", "value": [USERS[1]["email"], USERS[2]["email"], USERS[3]["email"]]},
]


@pytest.mark.parametrize("data", USERS_IN_LOOKUP, scope="function")
def test_get_list_in_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    users_repository = repository

    field = data["key"]
    lookup = f"{field}__in"
    expected_values = data["value"]
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        users_repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
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
def test_get_list_gt_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    field = data["key"]
    lookup = f"{field}__gt"
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
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
def test_get_list_gte_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = f"{field}__gte"
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
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
def test_get_list_lt_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = f"{field}__lt"
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
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
def test_get_list_lte_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    field = data["key"]
    lookup = f"{field}__lte"
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
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
def test_get_list_e_lookup_case_1(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = f"{field}__e"
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = getattr(user, field)
        assert value == data["value"]


@pytest.mark.parametrize("data", USERS_E_LOOKUP, scope="function")
def test_get_list_e_lookup_case_2(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = field
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
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
def test_get_list_ne_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = f"{field}__ne"
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
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
def test_get_list_not_in_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = f"{field}__not_in"
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
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
    {"key": "email", "value": "%gmail%"},
    {"key": "first_name", "value": "first%"},
    {"key": "last_name", "value": "%name%"},
]


@pytest.mark.parametrize("data", USERS_LIKE_LOOKUP, scope="function")
def test_get_list_like_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = f"{field}__like"
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = str(getattr(user, field))
        pattern = str(data["value"])
        if "%" in pattern:
            if pattern.startswith("%") and pattern.endswith("%"):
                assert pattern[1:-1] in value
            elif pattern.startswith("%"):
                assert value.endswith(pattern[1:])
            elif pattern.endswith("%"):
                assert value.startswith(pattern[:-1])
        else:
            assert pattern in value


USERS_NOT_LIKE_ALL_LOOKUP = [
    {"key": "id", "value": [USERS[0]["id"], USERS[1]["id"]]},
    {"key": "first_name", "value": ["name_1", "name_2"]},
    {
        "key": "email",
        "value": ["1_", "3_"],
    },
]


@pytest.mark.parametrize("data", USERS_NOT_LIKE_ALL_LOOKUP, scope="function")
def test_get_list_not_like_all_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = f"{field}__not_like_all"
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
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
def test_get_list_jsonb_like_lookup_case_1(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = f"{field}__jsonb_like"
    for value in data["value"]:
        items: List[Type[out_dataclass]] = e_loop.run_until_complete(
            repository.get_list(
                filter_data={lookup: value},
                out_dataclass=out_dataclass,
            )
        )

        assert isinstance(items, list) is True

        for index, user in enumerate(items):
            data = getattr(user, "meta", {})
            data_value = data.get(field)
            assert str(value) in str(data_value)


@pytest.mark.parametrize("data", USERS_JSONB_LIKE_LOOKUP, scope="function")
def test_get_list_jsonb_like_lookup_case_2(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = f"meta__{field}__jsonb_like"
    for value in data["value"]:
        items: List[Type[out_dataclass]] = e_loop.run_until_complete(
            repository.get_list(filter_data={lookup: value}, out_dataclass=out_dataclass)
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
def test_get_list_jsonb_not_like_lookup_case_1(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = f"{field}__jsonb_not_like"
    for value in data["value"]:
        items: List[Type[out_dataclass]] = e_loop.run_until_complete(
            repository.get_list(filter_data={lookup: value}, out_dataclass=out_dataclass)
        )

        assert isinstance(items, list) is True

        for index, user in enumerate(items):
            data = getattr(user, "meta", {})
            data_value = data.get(field)

            assert str(value) not in str(data_value)


@pytest.mark.parametrize("data", USERS_JSONB_NOT_LIKE_LOOKUP, scope="function")
def test_get_list_jsonb_not_like_lookup_case_2(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    field = data["key"]
    lookup = f"meta__{field}__jsonb_not_like"
    for value in data["value"]:
        items: List[Type[out_dataclass]] = e_loop.run_until_complete(
            repository.get_list(filter_data={lookup: value}, out_dataclass=out_dataclass)
        )

        assert isinstance(items, list) is True

        for index, user in enumerate(items):
            data = getattr(user, "meta", {})
            data_value = data.get(field)
            assert str(value) not in str(data_value)


USERS_ILIKE_LOOKUP = [
    {"key": "first_name", "value": "FIRST_NAME_1"},
    {"key": "first_name", "value": "first_name_2"},
    {"key": "email", "value": "GMAIL"},
    {"key": "email", "value": "1"},
    {"key": "last_name", "value": "LAST_NAME_3"},
    {"key": "email", "value": "%gmail%"},
    {"key": "first_name", "value": "first%"},
    {"key": "last_name", "value": "%name%"},
    {"key": "email", "value": "%.com"},
]


@pytest.mark.parametrize("data", USERS_ILIKE_LOOKUP, scope="function")
def test_get_list_ilike_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    field = data["key"]
    lookup = f"{field}__ilike"
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
    )

    assert isinstance(items, list) is True

    for index, user in enumerate(items):
        value = str(getattr(user, field)).lower()
        pattern = str(data["value"]).lower()
        if "%" in pattern:
            if pattern.startswith("%") and pattern.endswith("%"):
                assert pattern[1:-1] in value
            elif pattern.startswith("%"):
                assert value.endswith(pattern[1:])
            elif pattern.endswith("%"):
                assert value.startswith(pattern[:-1])
        else:
            assert pattern in value


USERS_EMPTY_FIELDS_LOOKUP = [
    {"key": "first_name", "value": ""},
    {"key": "email", "value": ""},
    {"key": "last_name", "value": ""},
]


@pytest.mark.parametrize("data", USERS_EMPTY_FIELDS_LOOKUP, scope="function")
def test_get_list_empty_string_lookup(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:
    field = data["key"]
    lookup = f"{field}__e"
    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data={lookup: data["value"]}, out_dataclass=out_dataclass)
    )

    assert isinstance(items, list) is True
    assert len(items) == 0


USERS_COMBINED_FILTERS_LOOKUP = [
    {"filters": {"first_name__like": "first_name", "id__gt": 1}, "expected_min_count": 1},
    {"filters": {"email__ilike": "GMAIL", "id__lte": 3}, "expected_min_count": 1},
    {"filters": {"first_name__e": USERS[0]["first_name"], "id__in": [1, 2, 3]}, "expected_min_count": 1},
]


@pytest.mark.parametrize("data", USERS_COMBINED_FILTERS_LOOKUP, scope="function")
def test_get_list_combined_filters(e_loop: AbstractEventLoop, users: Any, data: dict) -> None:

    items: List[Type[out_dataclass]] = e_loop.run_until_complete(
        repository.get_list(filter_data=data["filters"], out_dataclass=out_dataclass)
    )

    assert isinstance(items, list) is True
    assert len(items) >= data["expected_min_count"]
