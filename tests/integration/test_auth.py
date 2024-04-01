import pytest
from domain.auth_schemas import JwtTokenForm
from httpx import AsyncClient

sign_up_url = "/auth/signup"
login_url = "/auth/login"
refresh_url = "/auth/refresh-token"


class TestSignUp:

    @pytest.fixture(autouse=True)
    def async_client(self, ac: AsyncClient):
        self.client = ac

    async def test_signup_ok(self):
        response = await self.client.post(
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

    async def test_signup_user_already_exists(self):
        response = await self.client.post(
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

    async def test_signup_passwords_dont_match(self):
        response = await self.client.post(
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

    async def test_signup_invalid_data(self):
        response = await self.client.post(
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

    async def test_signup_incorrect_input(self):
        response = await self.client.post(
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


class TestLogin:

    @pytest.fixture(autouse=True)
    def async_client(self, ac: AsyncClient):
        self.client = ac

    @pytest.mark.parametrize(
        "identifier,password",
        [
            pytest.param("tolstoy@gmail.com", "Test19Test_", id="email"),
            pytest.param("yanomaly", "Test19Test_", id="username"),
            pytest.param("+375292291169", "Test19Test_", id="phone"),
        ],
    )
    async def test_login_ok(self, identifier: str, password: str):
        response = await self.client.post(
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

    async def test_login_no_user(self):
        response = await self.client.post(
            login_url,
            json={
                "identifier": "no_user",
                "password": "Test19Test_",
            },
        )

        assert response.status_code == 404, "Incorrect status code"
        assert response.json()["detail"] == "User doesn't exist", "Incorrect detail"

    async def test_login_invalid_identifier(self):
        response = await self.client.post(
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

    async def test_login_wrong_password(self):
        response = await self.client.post(
            login_url,
            json={
                "identifier": "yanomaly",
                "password": "Test22Test_",
            },
        )

        assert response.status_code == 422, "Incorrect status code"
        assert response.json()["detail"] == "Invalid credentials", "Incorrect detail"

    async def test_login_user_is_blocked(self):
        response = await self.client.post(
            login_url,
            json={
                "identifier": "blocked",
                "password": "Test19Test_",
            },
        )

        assert response.status_code == 422, "Incorrect status code"
        assert response.json()["detail"] == "User is blocked", "Incorrect detail"


class TestRefresh:

    @pytest.fixture(autouse=True)
    def async_client(self, ac: AsyncClient):
        self.client = ac

    @pytest.fixture(autouse=True)
    def valid_tokens(self, valid_tokens: list[JwtTokenForm]):
        self.tokens = valid_tokens

    async def test_refresh_ok(self):
        response = await self.client.post(
            refresh_url, headers={"Authorization": f"Bearer {self.tokens[1].token}"}
        )

        assert response.status_code == 200, "Incorrect status code"
        assert response.json()[0]["token"] is not None, "Incorrect access token"
        assert response.json()[0]["type"] == "access", "Incorrect access token type"
        assert response.json()[1]["token"] is not None, "Incorrect refresh token"
        assert response.json()[1]["type"] == "refresh", "Incorrect access token type"

    async def test_refresh_incorrect_token(self):
        response = await self.client.post(
            refresh_url,
            headers={
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJXaGl0ZU5pZ2h0c01hcmF0aG9uV2l0aEhvbm9yc0RpcGxvbWFJbkRhUG9ja2V0MTkifQ.BURHgBUsMXlWxnYLiZfPeScmltJ-D7DDMZqI5Hpaa_I"
            },
        )

        assert response.status_code == 403, "Incorrect status code"
