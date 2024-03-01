from auth.controller import validate_connection
from auth.dependencies import http_bearer
from dependencies import get_session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse
from users.controller import delete_user_db, update_user_db
from users.schemas import UpdateForm

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
