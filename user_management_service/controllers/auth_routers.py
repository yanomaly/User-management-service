from typing import Annotated, List

from dependencies import http_bearer
from domain.auth_schemas import JwtTokenForm, LogInForm, SignUpForm
from fastapi import APIRouter, Cookie, Depends
from fastapi.security import HTTPAuthorizationCredentials
from service.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/signup", response_model=JwtTokenForm, status_code=201)
async def sign_up(data: SignUpForm, auth_service: AuthService = Depends()):
    return await auth_service.sign_up(data)


@auth_router.post("/login", response_model=JwtTokenForm, status_code=200)
async def login(data: LogInForm, auth_service: AuthService = Depends()):
    return await auth_service.login(data)


@auth_router.post("/refresh-token", response_model=JwtTokenForm, status_code=200)
async def refresh_token(
    refresh: str | None = Cookie(default=None),
    auth_service: AuthService = Depends(),
):
    return await auth_service.refresh_tokens(refresh)
