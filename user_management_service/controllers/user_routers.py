from dependencies import get_session, http_bearer, redis_client
from domain.base import Pagination
from domain.user_schemas import UpdateForm, UserReturnForm
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from repository.queries.auth_repository import AuthRepository
from repository.queries.user_repository import UsersRepository
from service.users_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

user_router = APIRouter(prefix="/user", tags=["User"])
users_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get("/me", response_model=UserReturnForm, status_code=200)
async def get_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    return await UserService(
        AuthRepository(redis_client), UsersRepository(session)
    ).get_user_me(credentials)


@user_router.patch("/me", response_model=UserReturnForm, status_code=200)
async def update_user(
    data: UpdateForm,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    return await UserService(
        AuthRepository(redis_client), UsersRepository(session)
    ).update_user_me(credentials, data)


@user_router.delete("/me", response_model=UserReturnForm, status_code=200)
async def delete_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    return await UserService(
        AuthRepository(redis_client), UsersRepository(session)
    ).delete_user_me(credentials)


@user_router.get("/{user_id}", response_model=UserReturnForm, status_code=200)
async def get_user_by_id(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    return await UserService(
        AuthRepository(redis_client), UsersRepository(session)
    ).get_user_by_id(credentials, user_id)


@user_router.patch("/{user_id}", response_model=UserReturnForm, status_code=200)
async def update_user_by_id(
    user_id: str,
    data: UpdateForm,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    return await UserService(
        AuthRepository(redis_client), UsersRepository(session)
    ).update_user_by_id(credentials, user_id, data)


@users_router.get("/", response_model=list[UserReturnForm], status_code=200)
async def get_users_pagination(
    pagination: Pagination = Depends(),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    return await UserService(
        AuthRepository(redis_client), UsersRepository(session)
    ).paginate_users(credentials, pagination)
