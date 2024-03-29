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
def reset_token(validation_id) -> JwtTokenForm:
    return encode_reset_token(validation_id)


class Fixtures:
    @pytest.fixture(autouse=True)
    def async_client(self, ac: AsyncClient):
        self.client = ac

    @pytest.fixture(autouse=True)
    def valid_id(self, validation_id: str):
        self.id = validation_id

    @pytest.fixture(autouse=True)
    def valid_tokens(self, valid_tokens: list[JwtTokenForm]):
        self.tokens = valid_tokens

    @pytest.fixture(autouse=True)
    def tokens_to_delete(self, delete_tokens: list[JwtTokenForm]):
        self.delete_tokens = delete_tokens

    @pytest.fixture(autouse=True)
    def deletion_id(self, id_to_delete: str):
        self.delete_id = id_to_delete

    @pytest.fixture(autouse=True)
    def token_to_reset(self, reset_token: JwtTokenForm):
        self.reset = reset_token

    @pytest.fixture(autouse=True)
    def tokens_admin(self, admin_tokens: JwtTokenForm):
        self.admin = admin_tokens

    @pytest.fixture(autouse=True)
    def user_from_group(self, group_user_id: JwtTokenForm):
        self.group_user = group_user_id


class TestUserMe(Fixtures):
    async def test_get_user_me_ok(self):
        response = await self.client.get(
            me_url, headers={"Authorization": f"Bearer {self.tokens[0].token}"}
        )

        assert response.status_code == 200, "Incorrect status code"
        assert response.json()["id"] == self.id, "Incorrect returned id"

    async def test_update_user_me_ok(self):
        new_user_data = {
            "name": "Johh",
            "surname": "Janny",
            "username": "johnny",
            "phone_number": "+375291345678",
        }
        response = await self.client.patch(
            me_url,
            json=new_user_data,
            headers={"Authorization": f"Bearer {self.tokens[0].token}"},
        )

        assert response.status_code == 200, "Incorrect status code"
        assert response.json()["id"] == self.id, "Incorrect returned id"
        assert response.json()["name"] == new_user_data["name"], "Updated name"
        assert response.json()["surname"] == new_user_data["surname"], "Updated surname"
        assert (
            response.json()["username"] == new_user_data["username"]
        ), "Updated username"
        assert (
            response.json()["phone_number"] == new_user_data["phone_number"]
        ), "Updated phone"

    async def test_update_user_me_blank(self):
        new_user_data = {}
        response = await self.client.patch(
            me_url,
            json=new_user_data,
            headers={"Authorization": f"Bearer {self.tokens[0].token}"},
        )

        assert response.status_code == 200, "Incorrect status code"
        assert response.json()["id"] == self.id, "Incorrect returned id"

    async def test_forget_pass_ok(self):
        response = await self.client.post(forget_url, json={"identifier": "admin"})

        assert response.status_code == 200, "Incorrect status code"
        assert (
            response.json()["message"] == "Please, check your email!"
        ), "Incorrect message"

    async def test_forget_pass_blocked_user(self):
        response = await self.client.post(forget_url, json={"identifier": "blocked"})

        assert response.status_code == 422, "Incorrect status code"
        assert response.json()["detail"] == "User is blocked", "Incorrect message"

    async def test_forget_pass_no_user(self):
        response = await self.client.post(forget_url, json={"identifier": "yanomaly19"})

        assert response.status_code == 404, "Incorrect status code"
        assert response.json()["detail"] == "User doesn't exist", "Incorrect message"

    async def test_reset_pass_ok(self):
        new_password = {"password": "Test19Pass__", "password_repeat": "Test19Pass__"}
        response = await self.client.put(
            reset_url + f"/{self.reset.token}", json=new_password
        )

        assert response.status_code == 200, "Incorrect status code"
        assert (
            response.json()["message"] == "Password successfully updated"
        ), "Incorrect message"

    async def test_reset_pass_wrong_token(self):
        new_password = {"password": "Test19Pass__", "password_repeat": "Test19Pass__"}
        response = await self.client.put(
            reset_url + f"/{self.delete_tokens[0].token}", json=new_password
        )

        assert response.status_code == 401, "Incorrect status code"
        assert response.json()["detail"] == "Invalid token", "Incorrect detail"

    async def test_reset_pass_dont_match_pass(self):
        new_password = {"password": "Test19Pass__", "password_repeat": "Test19Pass"}
        response = await self.client.put(
            reset_url + f"/{self.reset.token}", json=new_password
        )

        assert response.status_code == 422, "Incorrect status code"
        assert (
            response.json()["detail"][0]["msg"] == "Value error, Passwords do not match"
        ), "Incorrect detail"

    async def test_delete_user_me_ok(self):
        response = await self.client.delete(
            me_url, headers={"Authorization": f"Bearer {self.delete_tokens[0].token}"}
        )

        assert response.status_code == 200, "Incorrect status code"
        assert response.json()["id"] == self.delete_id, "Incorrect returned id"

    async def test_delete_user_me_invalid_token(self):
        response = await self.client.delete(
            me_url, headers={"Authorization": f"Bearer {self.delete_tokens[0].token}"}
        )

        assert response.status_code == 401, "Incorrect status code"
        assert response.json()["detail"] == "Invalid token", "Incorrect detail"


class TestAdminModerFunctions(Fixtures):

    async def test_get_user_by_id_ok(self):
        response = await self.client.get(
            user_url + f"/{self.id}",
            headers={"Authorization": f"Bearer {self.tokens[0].token}"},
        )

        assert response.status_code == 200, "Incorrect status code"
        assert response.json()["id"] == self.id, "Incorrect returned id"

    async def test_get_user_by_id_one_group_ok(self):
        response = await self.client.get(
            user_url + f"/{self.group_user}",
            headers={"Authorization": f"Bearer {self.tokens[0].token}"},
        )

        assert response.status_code == 200, "Incorrect status code"
        assert response.json()["id"] == self.group_user, "Incorrect returned id"

    async def test_update_user_by_id_ok(self):
        new_user_data = {
            "name": "Iohannes",
            "surname": "Schneider",
            "username": "7000rpm",
            "phone_number": "+375446195568",
        }
        response = await self.client.patch(
            user_url + f"/{self.id}",
            json=new_user_data,
            headers={"Authorization": f"Bearer {self.admin[0].token}"},
        )

        assert response.status_code == 200, "Incorrect status code"
        assert response.json()["id"] == self.id, "Incorrect returned id"
        assert response.json()["name"] == new_user_data["name"], "Updated name"
        assert response.json()["surname"] == new_user_data["surname"], "Updated surname"
        assert (
            response.json()["username"] == new_user_data["username"]
        ), "Updated username"
        assert (
            response.json()["phone_number"] == new_user_data["phone_number"]
        ), "Updated phone"

    async def test_update_user_by_id_not_admin(self):
        new_user_data = {
            "name": "Iohannes",
            "surname": "Schneider",
            "username": "7000rpm",
            "phone_number": "+375446195568",
        }
        response = await self.client.patch(
            user_url + f"/{self.id}",
            json=new_user_data,
            headers={"Authorization": f"Bearer {self.tokens[0].token}"},
        )

        assert response.status_code == 403, "Incorrect status code"
        assert response.json()["detail"] == "You aren't admin", "Incorrect detail"

    async def test_pagination_admin_ok(self):
        page = 1
        per_page = 2
        response = await self.client.get(
            users_url + f"/?page={page}&per_page={per_page}",
            headers={"Authorization": f"Bearer {self.admin[0].token}"},
        )

        assert response.status_code == 200, "Incorrect status code"
        assert len(response.json()) == 2, "Incorrect number of items"

    async def test_pagination_admin_next_page_ok(self):
        page = 2
        per_page = 1
        response = await self.client.get(
            users_url + f"/?page={page}&per_page={per_page}",
            headers={"Authorization": f"Bearer {self.admin[0].token}"},
        )

        assert response.status_code == 200, "Incorrect status code"
        assert len(response.json()) == 1, "Incorrect number of items"

    async def test_pagination_admin_filter_ok(self):
        page = 1
        per_page = 2
        filter_by = "username"
        filter_value = "blocked"
        response = await self.client.get(
            users_url
            + f"/?page={page}&per_page={per_page}&filter_by={filter_by}&filter_value={filter_value}",
            headers={"Authorization": f"Bearer {self.admin[0].token}"},
        )

        assert response.status_code == 200, "Incorrect status code"
        assert len(response.json()) == 1, "Incorrect number of items"
        assert response.json()[0][filter_by] == filter_value, "Incorrect filtered item"

    async def test_pagination_moderator_ok(self):
        page = 1
        per_page = 3
        response = await self.client.get(
            users_url + f"/?page={page}&per_page={per_page}",
            headers={"Authorization": f"Bearer {self.tokens[0].token}"},
        )

        assert response.status_code == 200, "Incorrect status code"
        assert len(response.json()) == 2, "Incorrect number of items"

    async def test_get_user_by_id_no_user(self):
        response = await self.client.get(
            user_url + f"/{self.delete_id}",
            headers={"Authorization": f"Bearer {self.admin[0].token}"},
        )

        assert response.status_code == 404, "Incorrect status code"
        assert response.json()["detail"] == "User doesn't exist", "Incorrect detail"
