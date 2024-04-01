from unittest.mock import AsyncMock

import pytest
from models.user_models import User
from repository.user_repository import UsersRepository


@pytest.fixture(scope="module")
def user() -> User:
    return User(name="Dbtest", surname="Dbtest", username="db_user")


@pytest.fixture(scope="function")
def user_repo(user: User) -> UsersRepository:
    return UsersRepository(session=AsyncMock())


async def test_insert_ok(user_repo: UsersRepository, user: User):
    returned_user = await user_repo.insert(user)

    assert user_repo.session.add.call_count == 1, "Incorrect number of calls Add"
    assert user_repo.session.commit.call_count == 1, "Incorrect number of calls Commit"
    assert returned_user.name == user.name, "Incorrect inserted name"
    assert returned_user.surname == user.surname, "Incorrect inserted surname"
    assert returned_user.username == user.username, "Incorrect inserted username"
