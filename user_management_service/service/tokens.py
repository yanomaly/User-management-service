from datetime import datetime, timedelta
from typing import List

import jwt
from config import Settings
from domain.auth_schemas import JwtTokenForm
from fastapi import HTTPException

settings = Settings()


def encode_token(payload: dict, token_type) -> JwtTokenForm:
    return JwtTokenForm(
        token=jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256"),
        type=token_type,
    )


def encode_tokens(user_id: str) -> List[JwtTokenForm]:
    access_token = encode_token(
        {
            "sub": "access",
            "iss": user_id,
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES),
        },
        "access",
    )
    refresh_token = encode_token(
        {
            "sub": "refresh",
            "iss": user_id,
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRATION_MINUTES),
        },
        "refresh",
    )
    return [access_token, refresh_token]


def encode_reset_token(user_id: str) -> JwtTokenForm:
    return encode_token(
        {
            "sub": "reset",
            "iss": user_id,
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.RESET_TOKEN_EXPIRATION_MINUTES),
        },
        "reset",
    )


def decode_token(token: JwtTokenForm) -> dict:
    try:
        payload = jwt.decode(token.token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload["sub"] != token.type.value:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
