from typing import List, Optional

from domain.auth_schemas import JwtTokenForm, KeyValuePair, LogInForm, SignUpForm
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from models.user_models import User
from passlib.context import CryptContext
from repository.auth_repository import AuthRepository
from repository.user_repository import UsersRepository
from service.tokens import decode_token, encode_tokens
from sqlalchemy.exc import IntegrityError


class AuthService:
    def __init__(
        self,
        auth_repo: AuthRepository = Depends(),
        user_repo: UsersRepository = Depends(),
    ):
        self.auth_repo = auth_repo
        self.user_repo = user_repo

    async def sign_up(self, form: SignUpForm) -> List[JwtTokenForm]:
        user_to_insert = User(**form.dict(exclude={"password_repeat"}))
        user_to_insert.password = self.hash_password(form.password.get_secret_value())
        try:
            created_user = await self.user_repo.insert(user_to_insert)
        except IntegrityError:
            raise HTTPException(status_code=422, detail="User already exists")
        tokens = self.authenticate_user(form.password.get_secret_value(), created_user)
        return tokens

    async def login(self, form: LogInForm) -> List[JwtTokenForm]:
        logining_user = await self.user_repo.get_by(
            form.identifier, form.identifier_type
        )
        tokens = self.authenticate_user(form.password.get_secret_value(), logining_user)
        return tokens

    async def refresh_tokens(
        self, credentials: HTTPAuthorizationCredentials
    ) -> List[JwtTokenForm]:
        token = JwtTokenForm(token=credentials.credentials, type="refresh")
        user = await self.validate_connection(token)
        tokens = self.generate_new_tokens(token, user)
        return tokens

    def generate_new_tokens(
        self, token: JwtTokenForm, user: Optional[User]
    ) -> List[JwtTokenForm]:
        if (
            not user
            or user.is_blocked
            or self.check_if_blacklisted(str(user.id), token)
        ):
            raise HTTPException(status_code=401, detail="Invalid token")
        self.auth_repo.insert(KeyValuePair(key=str(user.id), value=token))
        return encode_tokens(str(user.id))

    async def validate_connection(self, token: JwtTokenForm) -> User:
        credentials = decode_token(token)
        user = await self.user_repo.get_by(credentials["iss"], "id")
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user

    def authenticate_user(
        self, form_password: str, user: Optional[User]
    ) -> List[JwtTokenForm]:
        if not user:
            raise HTTPException(status_code=404, detail="User doesn't exist")
        elif user.is_blocked:
            raise HTTPException(status_code=422, detail="User is blocked")
        elif not self.verify_password(form_password, user.password):
            raise HTTPException(status_code=422, detail="Invalid credentials")
        return encode_tokens(str(user.id))

    def check_if_blacklisted(self, user_id: str, token: JwtTokenForm) -> bool:
        user_tokens_blacklist = self.auth_repo.get_by_id(user_id)
        return token.token in user_tokens_blacklist.value

    @staticmethod
    def hash_password(password: str) -> str:
        return CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return CryptContext(schemes=["bcrypt"], deprecated="auto").verify(
            plain_password, hashed_password
        )
