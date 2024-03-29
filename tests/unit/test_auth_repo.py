from unittest.mock import Mock

import pytest
from domain.auth_schemas import KeyValuePair
from repository.auth_repository import AuthRepository


@pytest.fixture(scope="function")
def auth_repo() -> AuthRepository:
    return AuthRepository(redis=Mock(return_value=None))


@pytest.fixture(scope="function")
def key_value() -> KeyValuePair:
    return KeyValuePair(key="key", value=Mock())


def test_insert_ok(auth_repo: AuthRepository, key_value: KeyValuePair):
    inserted_pair = auth_repo.insert(key_value)

    assert auth_repo.redis.lpush.call_count == 1, "Incorrect number of calls lpush"
    assert inserted_pair.key == key_value.key, "Incorrect inserted key"
    assert inserted_pair.value == key_value.value, "Incorrect inserted value"


def test_get_by_id(auth_repo: AuthRepository, key_value: KeyValuePair):
    returned_value = auth_repo.get_by_id("id")

    assert auth_repo.redis.lrange.call_count == 1, "Incorrect number of calls lrange"
    assert returned_value.key == "id", "Incorrect returned id"
