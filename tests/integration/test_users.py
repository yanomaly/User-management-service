import pytest
from conftest import session_factory_test
from domain.auth_schemas import JwtTokenForm
from httpx import AsyncClient
from models.user_models import User
from service.tokens import encode_reset_token, encode_tokens
from sqlalchemy import select

user_url = "/user"
me_url = user_url + "/me"
image_url = me_url + "/image"
forget_url = me_url + "/forget"
reset_url = user_url + "/reset"

users_url = "/users"


@pytest.fixture(scope="function")
async def admin_tokens() -> list[JwtTokenForm]:
    async with session_factory_test() as session:
        query = select(User).where(User.username == "admin")
        query_result = await session.execute(query)
        admin = query_result.scalars().first()
        return encode_tokens(str(admin.id))


@pytest.fixture(scope="function")
async def group_user_id() -> str:
    async with session_factory_test() as session:
        query = select(User).where(User.username == "blocked")
        query_result = await session.execute(query)
        user = query_result.scalars().first()
        return str(user.id)


@pytest.fixture(scope="function")
async def reset_token(validation_id) -> JwtTokenForm:
    return encode_reset_token(validation_id)


async def test_get_user_me_ok(
    ac: AsyncClient, validation_id: str, valid_tokens: list[JwtTokenForm]
):
    response = await ac.get(
        me_url, headers={"Authorization": f"Bearer {valid_tokens[0].token}"}
    )

    assert response.status_code == 200, "Incorrect status code"
    assert response.json()["id"] == validation_id, "Incorrect returned id"


async def test_update_user_me_ok(
    ac: AsyncClient, validation_id: str, valid_tokens: list[JwtTokenForm]
):
    new_user_data = {
        "name": "Johh",
        "surname": "Janny",
        "username": "johnny",
        "phone_number": "+375291345678",
    }
    response = await ac.patch(
        me_url,
        json=new_user_data,
        headers={"Authorization": f"Bearer {valid_tokens[0].token}"},
    )

    assert response.status_code == 200, "Incorrect status code"
    assert response.json()["id"] == validation_id, "Incorrect returned id"
    assert response.json()["name"] == new_user_data["name"], "Updated name"
    assert response.json()["surname"] == new_user_data["surname"], "Updated surname"
    assert response.json()["username"] == new_user_data["username"], "Updated username"
    assert (
        response.json()["phone_number"] == new_user_data["phone_number"]
    ), "Updated phone"


async def test_update_user_me_blank(
    ac: AsyncClient, validation_id: str, valid_tokens: list[JwtTokenForm]
):
    new_user_data = {}
    response = await ac.patch(
        me_url,
        json=new_user_data,
        headers={"Authorization": f"Bearer {valid_tokens[0].token}"},
    )

    assert response.status_code == 200, "Incorrect status code"
    assert response.json()["id"] == validation_id, "Incorrect returned id"


async def test_forget_pass_ok(ac: AsyncClient):
    response = await ac.post(forget_url, json={"identifier": "admin"})

    assert response.status_code == 200, "Incorrect status code"
    assert (
        response.json()["message"] == "Please, check your email!"
    ), "Incorrect message"


async def test_forget_pass_blocked_user(ac: AsyncClient):
    response = await ac.post(forget_url, json={"identifier": "blocked"})

    assert response.status_code == 422, "Incorrect status code"
    assert response.json()["detail"] == "User is blocked", "Incorrect message"


async def test_forget_pass_no_user(ac: AsyncClient):
    response = await ac.post(forget_url, json={"identifier": "yanomaly19"})

    assert response.status_code == 404, "Incorrect status code"
    assert response.json()["detail"] == "User doesn't exist", "Incorrect message"


async def test_get_user_by_id_ok(
    ac: AsyncClient, admin_tokens: list[JwtTokenForm], validation_id: str
):
    response = await ac.get(
        user_url + f"/{validation_id}",
        headers={"Authorization": f"Bearer {admin_tokens[0].token}"},
    )

    assert response.status_code == 200, "Incorrect status code"
    assert response.json()["id"] == validation_id, "Incorrect returned id"


async def test_get_user_by_id_one_group_ok(
    ac: AsyncClient, group_user_id: str, valid_tokens: list[JwtTokenForm]
):
    response = await ac.get(
        user_url + f"/{group_user_id}",
        headers={"Authorization": f"Bearer {valid_tokens[0].token}"},
    )

    assert response.status_code == 200, "Incorrect status code"
    assert response.json()["id"] == group_user_id, "Incorrect returned id"


async def test_update_user_by_id_ok(
    ac: AsyncClient, admin_tokens: list[JwtTokenForm], validation_id: str
):
    new_user_data = {
        "name": "Iohannes",
        "surname": "Schneider",
        "username": "7000rpm",
        "phone_number": "+375446195568",
    }
    response = await ac.patch(
        user_url + f"/{validation_id}",
        json=new_user_data,
        headers={"Authorization": f"Bearer {admin_tokens[0].token}"},
    )

    assert response.status_code == 200, "Incorrect status code"
    assert response.json()["id"] == validation_id, "Incorrect returned id"
    assert response.json()["name"] == new_user_data["name"], "Updated name"
    assert response.json()["surname"] == new_user_data["surname"], "Updated surname"
    assert response.json()["username"] == new_user_data["username"], "Updated username"
    assert (
        response.json()["phone_number"] == new_user_data["phone_number"]
    ), "Updated phone"


async def test_update_user_by_id_not_admin(
    ac: AsyncClient, valid_tokens: list[JwtTokenForm], validation_id: str
):
    new_user_data = {
        "name": "Iohannes",
        "surname": "Schneider",
        "username": "7000rpm",
        "phone_number": "+375446195568",
    }
    response = await ac.patch(
        user_url + f"/{validation_id}",
        json=new_user_data,
        headers={"Authorization": f"Bearer {valid_tokens[0].token}"},
    )

    assert response.status_code == 403, "Incorrect status code"
    assert response.json()["detail"] == "You aren't admin", "Incorrect detail"


async def test_pagination_admin_ok(ac: AsyncClient, admin_tokens: list[JwtTokenForm]):
    page = 1
    per_page = 2
    response = await ac.get(
        users_url + f"/?page={page}&per_page={per_page}",
        headers={"Authorization": f"Bearer {admin_tokens[0].token}"},
    )

    assert response.status_code == 200, "Incorrect status code"
    assert len(response.json()) == 2, "Incorrect number of items"


async def test_pagination_admin_next_page_ok(
    ac: AsyncClient, admin_tokens: list[JwtTokenForm]
):
    page = 2
    per_page = 1
    response = await ac.get(
        users_url + f"/?page={page}&per_page={per_page}",
        headers={"Authorization": f"Bearer {admin_tokens[0].token}"},
    )

    assert response.status_code == 200, "Incorrect status code"
    assert len(response.json()) == 1, "Incorrect number of items"


async def test_pagination_admin_filter_ok(
    ac: AsyncClient, admin_tokens: list[JwtTokenForm]
):
    page = 1
    per_page = 2
    filter_by = "username"
    filter_value = "blocked"
    response = await ac.get(
        users_url
        + f"/?page={page}&per_page={per_page}&filter_by={filter_by}&filter_value={filter_value}",
        headers={"Authorization": f"Bearer {admin_tokens[0].token}"},
    )

    assert response.status_code == 200, "Incorrect status code"
    assert len(response.json()) == 1, "Incorrect number of items"
    assert response.json()[0][filter_by] == filter_value, "Incorrect filtered item"


async def test_pagination_moderator_ok(
    ac: AsyncClient, valid_tokens: list[JwtTokenForm]
):
    page = 1
    per_page = 3
    response = await ac.get(
        users_url + f"/?page={page}&per_page={per_page}",
        headers={"Authorization": f"Bearer {valid_tokens[0].token}"},
    )

    assert response.status_code == 200, "Incorrect status code"
    assert len(response.json()) == 2, "Incorrect number of items"


async def test_reset_pass_ok(ac: AsyncClient, reset_token: JwtTokenForm):
    new_password = {"password": "Test19Pass__", "password_repeat": "Test19Pass__"}
    response = await ac.put(reset_url + f"/{reset_token.token}", json=new_password)

    assert response.status_code == 200, "Incorrect status code"
    assert (
        response.json()["message"] == "Password successfully updated"
    ), "Incorrect message"


async def test_reset_pass_wrong_token(
    ac: AsyncClient, admin_tokens: list[JwtTokenForm]
):
    new_password = {"password": "Test19Pass__", "password_repeat": "Test19Pass__"}
    response = await ac.put(reset_url + f"/{admin_tokens[0].token}", json=new_password)

    assert response.status_code == 401, "Incorrect status code"
    assert response.json()["detail"] == "Invalid token", "Incorrect detail"


async def test_reset_pass_dont_match_pass(ac: AsyncClient, reset_token: JwtTokenForm):
    new_password = {"password": "Test19Pass__", "password_repeat": "Test19Pass"}
    response = await ac.put(reset_url + f"/{reset_token.token}", json=new_password)

    assert response.status_code == 422, "Incorrect status code"
    assert (
        response.json()["detail"][0]["msg"] == "Value error, Passwords do not match"
    ), "Incorrect detail"


async def test_delete_user_me_ok(
    ac: AsyncClient, validation_id: str, valid_tokens: list[JwtTokenForm]
):
    response = await ac.delete(
        me_url, headers={"Authorization": f"Bearer {valid_tokens[0].token}"}
    )

    assert response.status_code == 200, "Incorrect status code"
    assert response.json()["id"] == validation_id, "Incorrect returned id"


async def test_delete_user_me_invalid_token(
    ac: AsyncClient, valid_tokens: list[JwtTokenForm]
):
    response = await ac.delete(
        me_url, headers={"Authorization": f"Bearer {valid_tokens[0].token}"}
    )

    assert response.status_code == 401, "Incorrect status code"
    assert response.json()["detail"] == "Invalid token", "Incorrect detail"


async def test_get_user_by_id_no_user(
    ac: AsyncClient, admin_tokens: list[JwtTokenForm], validation_id: str
):
    response = await ac.get(
        user_url + f"/{validation_id}",
        headers={"Authorization": f"Bearer {admin_tokens[0].token}"},
    )

    assert response.status_code == 404, "Incorrect status code"
    assert response.json()["detail"] == "User doesn't exist", "Incorrect detail"
