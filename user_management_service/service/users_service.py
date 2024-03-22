from datetime import datetime

from dependencies import settings
from domain.auth_schemas import ForgetForm, JwtTokenForm, ResetPassword
from domain.base import Pagination, RabbitMessageBody, ReturnMessage
from domain.user_schemas import UpdateForm, UserReturnForm
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from models.user_models import User
from repository.auth_repository import AuthRepository
from repository.pagination import PaginationRepo
from repository.rabbit_repo import RabbitRepository
from repository.user_repository import UsersRepository
from service.auth_service import AuthService
from service.tokens import decode_token, encode_reset_token


class UserService:
    def __init__(
        self,
        auth_repo: AuthRepository = Depends(),
        user_repo: UsersRepository = Depends(),
        rabbit_repo: RabbitRepository = Depends(),
    ):
        self.auth_repo = auth_repo
        self.user_repo = user_repo
        self.rabbit_repo = rabbit_repo

    async def get_user_me(
        self, credentials: HTTPAuthorizationCredentials
    ) -> UserReturnForm:
        session_user = await AuthService(
            self.auth_repo, self.user_repo
        ).validate_connection(
            JwtTokenForm(token=credentials.credentials, type="access")
        )
        return session_user

    async def update_user_me(
        self, credentials: HTTPAuthorizationCredentials, data: UpdateForm
    ) -> UserReturnForm:
        session_user = await AuthService(
            self.auth_repo, self.user_repo
        ).validate_connection(
            JwtTokenForm(token=credentials.credentials, type="access")
        )
        updated_user = await self.user_repo.update(
            self.create_update_user(data, session_user)
        )
        return updated_user

    async def delete_user_me(
        self, credentials: HTTPAuthorizationCredentials
    ) -> UserReturnForm:
        session_user = await AuthService(
            self.auth_repo, self.user_repo
        ).validate_connection(
            JwtTokenForm(token=credentials.credentials, type="access")
        )
        deleted_user = await self.user_repo.delete(str(session_user.id))
        return deleted_user

    async def get_user_by_id(
        self, credentials: HTTPAuthorizationCredentials, user_id: str
    ) -> UserReturnForm:
        session_user = await AuthService(
            self.auth_repo, self.user_repo
        ).validate_connection(
            JwtTokenForm(token=credentials.credentials, type="access")
        )
        user_to_return = await self.user_repo.get_by_id(user_id)
        if not UserService.if_group_moderator(
            session_user, str(user_to_return.group_id)
        ) or UserService.if_moderator(session_user):
            raise HTTPException(
                status_code=403, detail="You aren't moderator or admin of user's group"
            )
        return user_to_return

    async def update_user_by_id(
        self, credentials: HTTPAuthorizationCredentials, user_id: str, data: UpdateForm
    ) -> UserReturnForm:
        session_user = await AuthService(
            self.auth_repo, self.user_repo
        ).validate_connection(
            JwtTokenForm(token=credentials.credentials, type="access")
        )
        user_to_update = await self.user_repo.get_by_id(user_id)
        if not UserService.if_admin(session_user):
            raise HTTPException(status_code=403, detail="You aren't admin")
        updated_user = await self.user_repo.update(
            self.create_update_user(data, user_to_update)
        )
        return updated_user

    async def paginate_users(
        self, credentials: HTTPAuthorizationCredentials, pagination: Pagination
    ) -> list[UserReturnForm]:
        session_user = await AuthService(
            self.auth_repo, self.user_repo
        ).validate_connection(
            JwtTokenForm(token=credentials.credentials, type="access")
        )
        if not self.if_admin(session_user) or not self.if_moderator(session_user):
            raise HTTPException(status_code=403, detail="You aren't admin or moderator")
        filters = {}
        if pagination.filter_by and pagination.filter_value:
            filters.update({pagination.filter_by: pagination.filter_value})
        if self.if_moderator(session_user):
            filters.update({"group_id": session_user.group_id})
        return await PaginationRepo(self.user_repo.session).paginate(
            User, pagination, filters
        )

    async def forget_password(self, data: ForgetForm) -> ReturnMessage:
        user = await self.user_repo.get_by(data.identifier, data.identifier_type)
        self.check_user(user)
        reset_token = encode_reset_token(str(user.id))
        reset_url = f"http://{settings.APP_HOST}:{settings.APP_PORT}/user/reset/{reset_token.token}"
        self.rabbit_repo.send_message(
            settings.ROUTING_KEY,
            {"retries": 0},
            RabbitMessageBody(
                link=reset_url, email=user.email, publishing_time=datetime.utcnow()
            ).model_dump_json(),
        )
        return ReturnMessage(message="Please, check your email!")

    async def reset_password(self, token: str, data: ResetPassword) -> ReturnMessage:
        payload = decode_token(JwtTokenForm(token=token, type="reset"))
        user_to_update = await self.user_repo.get_by_id(payload.get("iss"))
        self.check_user(user_to_update)
        if AuthService.verify_password(
            data.password.get_secret_value(), user_to_update.password
        ):
            raise HTTPException(
                status_code=422,
                detail="New password should be different with old password",
            )
        user_to_update.password = AuthService.hash_password(
            data.password.get_secret_value()
        )
        await self.user_repo.update(user_to_update)
        return ReturnMessage(message="Password successfully updated")

    @staticmethod
    def check_user(user: User) -> None:
        if not user:
            raise HTTPException(status_code=404, detail="User doesn't exist")
        elif user.is_blocked:
            raise HTTPException(status_code=422, detail="User is blocked")

    @staticmethod
    def create_update_user(data: UpdateForm, user: User) -> User:
        for key, value in data.dict(exclude_unset=True).items():
            setattr(user, key, value)
        return user

    @staticmethod
    def if_group_moderator(user: User, group_id: str) -> bool:
        return UserService.if_in_group(user, group_id) and UserService.if_moderator(
            user
        )

    @staticmethod
    def if_in_group(user: User, group_id: str) -> bool:
        return user and group_id and user.group_id == group_id

    @staticmethod
    def if_admin(user: User) -> bool:
        return user and user.role.value == "admin"

    @staticmethod
    def if_moderator(user: User) -> bool:
        return user and user.role.value == "moderator"
