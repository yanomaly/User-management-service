import pytest
from domain.auth_schemas import JwtTokenForm
from httpx import AsyncClient

sign_up_url = "/auth/signup"
login_url = "/auth/login"
refresh_url = "/auth/refresh-token"


async def test_signup_ok(ac: AsyncClient):
    response = await ac.post(
        sign_up_url,
        json={
            "name": "Yan",
            "surname": "Tolstoy",
            "username": "yanomaly",
            "email": "tolstoy@gmail.com",
            "phone_number": "+375292291169",
            "password": "Test19Test_",
            "password_repeat": "Test19Test_",
        },
    )

    assert response.status_code == 201, "Incorrect status code"
    assert response.json()[0]["token"] is not None, "Incorrect access token"
    assert response.json()[0]["type"] == "access", "Incorrect access token type"
    assert response.json()[1]["token"] is not None, "Incorrect refresh token"
    assert response.json()[1]["type"] == "refresh", "Incorrect access token type"


async def test_signup_user_already_exists(ac: AsyncClient):
    response = await ac.post(
        sign_up_url,
        json={
            "name": "Yan",
            "surname": "Tolstoy",
            "username": "yanomaly",
            "email": "tolstoy@gmail.com",
            "phone_number": "+375292291169",
            "password": "Test19Test_",
            "password_repeat": "Test19Test_",
        },
    )

    assert response.status_code == 422, "Incorrect status code"
    assert response.json()["detail"] == "User already exists", "Incorrect detail"


async def test_signup_passwords_dont_match(ac: AsyncClient):
    response = await ac.post(
        sign_up_url,
        json={
            "name": "Yan",
            "surname": "Tolstoy",
            "username": "yanomaly",
            "email": "tolstoy@gmail.com",
            "phone_number": "+375292291169",
            "password": "Test19Test_",
            "password_repeat": "Test22Test_",
        },
    )

    assert response.status_code == 422, "Incorrect status code"
    assert (
        response.json()["detail"][0]["msg"] == "Value error, Passwords do not match"
    ), "Incorrect detail"


async def test_signup_invalid_data(ac: AsyncClient):
    response = await ac.post(
        sign_up_url,
        json={
            "name": "yan",
            "surname": "Шнайдер",
            "username": "yano maly",
            "email": ".gmail.com",
            "phone_number": "+49296422969",
            "password": "Test19Test_",
            "password_repeat": "Test19Test_",
        },
    )

    assert response.status_code == 422, "Incorrect status code"
    assert len(response.json()["detail"]) == 5, "Incorrect detail"


async def test_signup_incorrect_input(ac: AsyncClient):
    response = await ac.post(
        sign_up_url,
        json={
            "name": "Yan",
            "email": "tolstoy@gmail.com",
            "phone_number": "+375292291169",
            "password": "Test19Test_",
            "password_repeat": "Test19Test_",
        },
    )

    assert response.status_code == 422, "Incorrect status code"
    assert response.json()["detail"][0]["msg"] == "Field required", "Incorrect msg"


@pytest.mark.parametrize(
    "identifier,password",
    [
        pytest.param("tolstoy@gmail.com", "Test19Test_", id="email"),
        pytest.param("yanomaly", "Test19Test_", id="username"),
        pytest.param("+375292291169", "Test19Test_", id="phone"),
    ],
)
async def test_login_ok(ac: AsyncClient, identifier: str, password: str):
    response = await ac.post(
        login_url,
        json={
            "identifier": identifier,
            "password": password,
        },
    )

    assert response.status_code == 200, "Incorrect status code"
    assert response.json()[0]["token"] is not None, "Incorrect access token"
    assert response.json()[0]["type"] == "access", "Incorrect access token type"
    assert response.json()[1]["token"] is not None, "Incorrect refresh token"
    assert response.json()[1]["type"] == "refresh", "Incorrect access token type"


async def test_login_no_user(ac: AsyncClient):
    response = await ac.post(
        login_url,
        json={
            "identifier": "no_user",
            "password": "Test19Test_",
        },
    )

    assert response.status_code == 404, "Incorrect status code"
    assert response.json()["detail"] == "User doesn't exist", "Incorrect detail"


async def test_login_invalid_identifier(ac: AsyncClient):
    response = await ac.post(
        login_url,
        json={
            "identifier": "In149VAAAAAAAAAAAAAAAaalidddd  )_",
            "password": "Test19Test_",
        },
    )

    assert response.status_code == 422, "Incorrect status code"
    assert (
        response.json()["detail"][0]["msg"]
        == "Value error, Username, phone number or email isn't correct"
    ), "Incorrect message"


async def test_login_wrong_password(ac: AsyncClient):
    response = await ac.post(
        login_url,
        json={
            "identifier": "yanomaly",
            "password": "Test22Test_",
        },
    )

    assert response.status_code == 422, "Incorrect status code"
    assert response.json()["detail"] == "Invalid credentials", "Incorrect detail"


async def test_login_user_is_blocked(ac: AsyncClient):
    response = await ac.post(
        login_url,
        json={
            "identifier": "blocked",
            "password": "Test19Test_",
        },
    )

    assert response.status_code == 422, "Incorrect status code"
    assert response.json()["detail"] == "User is blocked", "Incorrect detail"


async def test_refresh_ok(ac: AsyncClient, valid_tokens: list[JwtTokenForm]):
    response = await ac.post(
        refresh_url, headers={"Authorization": f"Bearer {valid_tokens[1].token}"}
    )

    assert response.status_code == 200, "Incorrect status code"
    assert response.json()[0]["token"] is not None, "Incorrect access token"
    assert response.json()[0]["type"] == "access", "Incorrect access token type"
    assert response.json()[1]["token"] is not None, "Incorrect refresh token"
    assert response.json()[1]["type"] == "refresh", "Incorrect access token type"


async def test_refresh_incorrect_token(ac: AsyncClient):
    response = await ac.post(
        refresh_url,
        headers={
            "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJXaGl0ZU5pZ2h0c01hcmF0aG9uV2l0aEhvbm9yc0RpcGxvbWFJbkRhUG9ja2V0MTkifQ.BURHgBUsMXlWxnYLiZfPeScmltJ-D7DDMZqI5Hpaa_I"
        },
    )

    assert response.status_code == 403, "Incorrect status code"
