from typing import List

from dependencies import get_session, http_bearer, redis_client
from domain.auth_schemas import JwtTokenForm, LogInForm, SignUpForm
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from repository.queries.auth_repository import AuthRepository
from repository.queries.user_repository import UsersRepository
from service.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/signup", response_model=list[JwtTokenForm], status_code=201)
async def sign_up(data: SignUpForm, session: AsyncSession = Depends(get_session)):
    return await AuthService(
        AuthRepository(redis_client), UsersRepository(session)
    ).sign_up(data)


@auth_router.post("/login", response_model=List[JwtTokenForm], status_code=200)
async def login(data: LogInForm, session: AsyncSession = Depends(get_session)):
    return await AuthService(
        AuthRepository(redis_client), UsersRepository(session)
    ).login(data)


@auth_router.post("/refresh-token", response_model=List[JwtTokenForm], status_code=200)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
):
    return await AuthService(
        AuthRepository(redis_client), UsersRepository(session)
    ).refresh_tokens(credentials)
