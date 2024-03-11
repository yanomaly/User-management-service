import logging

import redis
from config import Settings
from database import session_factory
from fastapi.security import HTTPBearer

logging.config.fileConfig("./logger.ini")
auth_logger = logging.getLogger("auth")

settings = Settings()

http_bearer = HTTPBearer()

redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
)


async def get_session():
    async with session_factory() as session:
        yield session
