from domain.auth_schemas import JwtTokenForm
from domain.base import Pagination
from domain.user_schemas import UpdateForm, UserReturnForm
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from models.user_models import User
from repository.auth_repository import AuthRepository
from repository.pagination import PaginationRepo
from repository.user_repository import UsersRepository
from service.auth_service import AuthService


class UserService:
    def __init__(
        self,
        auth_repo: AuthRepository = Depends(),
        user_repo: UsersRepository = Depends(),
    ):
        self.auth_repo = auth_repo
        self.user_repo = user_repo

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

    @staticmethod
    def create_update_user(data: UpdateForm, user: User) -> User:
        for key, value in data.dict(exclude_unset=True).items():
            setattr(user, key, value)
        return user

    @staticmethod
    def if_group_moderator(user: User, group_id: str):
        return UserService.if_in_group(user, group_id) and UserService.if_moderator(
            user
        )

    @staticmethod
    def if_in_group(user: User, group_id: str):
        return user and group_id and user.group_id == group_id

    @staticmethod
    def if_admin(user: User):
        return user and user.role.value == "admin"

    @staticmethod
    def if_moderator(user: User):
        return user and user.role.value == "moderator"
