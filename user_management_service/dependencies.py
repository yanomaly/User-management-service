import logging

import aioboto3
import redis
from config import Settings
from database import session_factory
from fastapi.security import HTTPBearer

logging.config.fileConfig("../logger.ini")
auth_logger = logging.getLogger("auth")
users_logger = logging.getLogger("users")
base_logger = logging.getLogger("base")

settings = Settings()

http_bearer = HTTPBearer()

redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
)

aws_session = aioboto3.Session()


def get_redis_client():
    return redis_client


async def get_session():
    async with session_factory() as session:
        yield session


async def get_s3_client():
    async with aws_session.client(
        service_name="s3",
        region_name=settings.DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=f"http://{settings.HOSTNAME_EXTERNAL}:{settings.LOCALSTACK_PORT}",
    ) as client:
        yield client
