from auth.controller import validate_connection
from auth.dependencies import http_bearer
from dependencies import get_session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials
from schemas import Pagination
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse
from users.controller import (
    delete_user_db,
    find_user_db,
    if_admin,
    if_group_admin_or_moderator,
    paginate_users,
    update_user_db,
)
from users.schemas import ReturnForm, UpdateForm

user_router = APIRouter(prefix="/user")
users_router = APIRouter(prefix="/users")


@user_router.get("/me")
async def get_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    user = await validate_connection(credentials.credentials, "access", session)
    if not user:
        raise HTTPException(status_code=404, detail="User doesn't exist")
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"user": jsonable_encoder(user, exclude={"password"})},
    )
    return response


@user_router.patch("/me")
async def update_user(
    data: UpdateForm,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    user = await validate_connection(credentials.credentials, "access", session)
    if not user:
        raise HTTPException(status_code=404, detail="User doesn't exist")
    updated_user = await update_user_db(user, data, session)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "user": jsonable_encoder(updated_user, exclude={"password"}),
            "message": "Successfully updated",
        },
    )
    return response


@user_router.delete("/me")
async def delete_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    user = await validate_connection(credentials.credentials, "access", session)
    await delete_user_db(str(user.id), session)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"user_id": str(user.id), "message": "Successfully deleted"},
    )
    return response


@user_router.get("/{user_id}")
async def get_user_by_id(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    verifiable_user = await validate_connection(
        credentials.credentials, "access", session
    )
    user = await find_user_db("id", user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User doesn't exist")
    if not if_group_admin_or_moderator(verifiable_user, str(user.group_id)):
        raise HTTPException(
            status_code=403,
            detail="You are not moderator or administrator of group that user belongs to",
        )
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"user": jsonable_encoder(user, exclude={"password"})},
    )
    return response


@user_router.patch("/{user_id}")
async def update_user_by_id(
    user_id: str,
    data: UpdateForm,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    verifiable_user = await validate_connection(
        credentials.credentials, "access", session
    )
    user = await find_user_db("id", user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User doesn't exist")
    if not if_admin(verifiable_user):
        raise HTTPException(status_code=403, detail="You aren't an admin")
    updated_user = await update_user_db(user, data, session)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "user": jsonable_encoder(updated_user, exclude={"password"}),
            "message": "Successfully updated",
        },
    )
    return response


@users_router.get("/", response_model=list[ReturnForm], status_code=200)
async def get_users_pagination(
    pagination: Pagination = Depends(),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    user = await validate_connection(credentials.credentials, "access", session)
    return await paginate_users(user, pagination, session)
