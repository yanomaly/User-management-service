from dependencies import get_session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from .controller import (
    authenticate_user,
    create_user,
    find_user_db,
    generate_new_tokens,
    validate_connection,
)
from .dependencies import http_bearer
from .schemas import LogInForm, SignUpForm

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/signup")
async def signup(data: SignUpForm, session: AsyncSession = Depends(get_session)):
    try:
        user = await create_user(data, session)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    access_token, refresh_token = authenticate_user(
        data.password.get_secret_value(), user
    )
    response = JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": str(user.id),
            },
            "message": "Successfully registered",
        },
    )
    return response


@auth_router.post("/login")
async def login(data: LogInForm, session: AsyncSession = Depends(get_session)):
    user = await find_user_db(data.identifier_type, data.identifier, session)
    access_token, refresh_token = authenticate_user(
        data.password.get_secret_value(), user
    )
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "data": {"access_token": access_token, "refresh_token": refresh_token},
            "message": "Successfully logged in",
        },
    )
    return response


@auth_router.post("/refresh-token")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    user = await validate_connection(credentials.credentials, "refresh", session)
    access_token, refresh_token = generate_new_tokens(credentials.credentials, user)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "data": {"access_token": access_token, "refresh_token": refresh_token},
            "message": "Successfully created new tokens",
        },
    )
    return response
