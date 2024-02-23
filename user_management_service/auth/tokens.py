from datetime import datetime, timedelta

import jwt
from config import Settings
from fastapi import HTTPException

settings = Settings()


def encode_token(user_id: str, token_type: str):
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

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def encode_tokens(user_id: str):
    access_token = encode_token(user_id, "access")
    refresh_token = encode_token(user_id, "refresh")

    return access_token, refresh_token


def decode_token(token: str, token_type: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload["sub"] != token_type:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload["iss"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
