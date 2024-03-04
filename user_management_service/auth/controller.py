from typing import Optional

from fastapi import HTTPException
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from users.controller import find_user_db
from users.model import Role, User

from .dependencies import redis_client
from .schemas import SignUpForm
from .tokens import decode_token, encode_tokens


def generate_new_tokens(token: str, user: Optional[User]):
    if not user or user.is_blocked or check_if_blacklisted(str(user.id), token):
        raise HTTPException(status_code=401, detail="Invalid token")
    add_to_blacklist(str(user.id), token)
    return encode_tokens(str(user.id))


def check_if_blacklisted(user_id: str, token: str):
    user_tokens_blacklist_len = redis_client.llen(user_id)
    if user_tokens_blacklist_len > 0:
        user_tokens_blacklist = redis_client.lrange(user_id, 0, -1)
        return token in user_tokens_blacklist


def add_to_blacklist(user_id: str, token: str):
    redis_client.lpush(user_id, token)


async def validate_connection(token: str, token_type: str, session: AsyncSession):
    try:
        user = await find_user_db("id", decode_token(token, token_type), session)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


def authenticate_user(form_password: str, user: Optional[User]):
    if not user:
        raise HTTPException(status_code=404, detail="User doesn't exist")
    elif user.is_blocked:
        raise HTTPException(status_code=400, detail="User is blocked")
    elif not verify_password(form_password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return encode_tokens(str(user.id))


async def create_user(form: SignUpForm, session: AsyncSession):
    user = User(
        name=form.name,
        surname=form.surname,
        username=form.username,
        password=get_password_hash(form.password.get_secret_value()),
        email=form.email,
        phone_number=form.phone_number,
        role=Role.USER,
    )
    session.add(user)
    await session.commit()
    return user


def get_password_hash(password: str):
    return CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return CryptContext(schemes=["bcrypt"], deprecated="auto").verify(
        plain_password, hashed_password
    )
