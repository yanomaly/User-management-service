from datetime import datetime, timedelta
from typing import List

import jwt
from config import Settings
from domain.auth_schemas import JwtTokenForm
from fastapi import HTTPException

settings = Settings()


def encode_token(user_id: str, token_type: str) -> JwtTokenForm:
    payload = dict(iss=user_id, sub=token_type)
    if token_type == "access":
        payload.update(
            {
                "exp": datetime.utcnow()
                + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES)
            }
        )
    else:
        payload.update(
            {
                "exp": datetime.utcnow()
                + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRATION_MINUTES)
            }
        )

    return JwtTokenForm(
        token=jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256"),
        type=token_type,
    )


def encode_tokens(user_id: str) -> List[JwtTokenForm]:
    access_token = encode_token(user_id, "access")
    refresh_token = encode_token(user_id, "refresh")
    return [access_token, refresh_token]


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
