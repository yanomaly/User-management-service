from dependencies import settings
from domain.auth_schemas import JwtTokenForm
from domain.base import Pagination
from domain.user_schemas import UpdateForm, UserReturnForm
from fastapi import Depends, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from models.user_models import User
from repository.aws_repository import S3Repo
from repository.pagination import PaginationRepo
from repository.user_repository import UsersRepository
from service.auth_service import AuthService


class UserService:
    def __init__(
        self,
        user_repo: UsersRepository = Depends(),
        auth_repo: AuthService = Depends(),
        s3_repo: S3Repo = Depends(),
    ):
        self.user_repo = user_repo
        self.auth_repo = auth_repo
        self.s3_repo = s3_repo

    async def get_user_me(
        self, credentials: HTTPAuthorizationCredentials
    ) -> UserReturnForm:
        session_user = await AuthService(
            self.auth_repo, self.user_repo
        ).validate_connection(
            JwtTokenForm(token=credentials.credentials, type="access")
        )
        session_user.image = await self.s3_repo.create_presigned_url(
            settings.BUCKET_NAME, session_user.image
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
        updated_user.image = await self.s3_repo.create_presigned_url(
            settings.BUCKET_NAME, updated_user.image
        )
        return updated_user

    async def upload_image_me(
        self, credentials: HTTPAuthorizationCredentials, image: UploadFile
    ) -> UserReturnForm:
        session_user = await AuthService(
            self.auth_repo, self.user_repo
        ).validate_connection(
            JwtTokenForm(token=credentials.credentials, type="access")
        )
        if not self.validate_image(image):
            raise HTTPException(status_code=400, detail="This image does not supported")
        await self.s3_repo.insert(image)
        session_user.image = image.filename
        updated_user = await self.user_repo.update(session_user)
        updated_user.image = await self.s3_repo.create_presigned_url(
            settings.BUCKET_NAME, updated_user.image
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
        user_to_return.image = await self.s3_repo.create_presigned_url(
            settings.BUCKET_NAME, user_to_return.image
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
        updated_user.image = await self.s3_repo.create_presigned_url(
            settings.BUCKET_NAME, updated_user.image
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
        if not self.if_admin(session_user) and not self.if_moderator(session_user):
            raise HTTPException(status_code=403, detail="You aren't admin or moderator")
        filters = {}
        if pagination.filter_by and pagination.filter_value:
            filters.update({pagination.filter_by: pagination.filter_value})
        if self.if_moderator(session_user):
            filters.update({"group_id": session_user.group_id})
        users_page = await PaginationRepo(self.user_repo.session).paginate(
            User, pagination, filters
        )
        for user in users_page:
            user.image = await self.s3_repo.create_presigned_url(
                settings.BUCKET_NAME, user.image
            )
        return users_page

    @staticmethod
    def validate_image(image: UploadFile) -> bool:
        types = ["image/png", "image/jpeg", "image/jpg", "application/pdf"]
        if image.content_type not in types or image.size > 1e7:
            return False
        else:
            return True

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
