import logging.config

import aioboto3
import redis
from botocore.client import BaseClient
from config import Settings
from database import session_factory
from fastapi.security import HTTPBearer
from pika.adapters.blocking_connection import BlockingConnection
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials
from pika.exceptions import AMQPError
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

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


def get_redis_client() -> Redis:
    return redis_client


async def get_session() -> AsyncSession:
    async with session_factory() as session:
        yield session


async def get_s3_client() -> BaseClient:
    async with aws_session.client(
        service_name="s3",
        region_name=settings.DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=f"http://{settings.HOSTNAME_EXTERNAL}:{settings.LOCALSTACK_PORT}",
    ) as client:
        yield client


class RabbitMQClient:
    def __init__(self):
        self.connection = self.create_connection()

    @staticmethod
    def create_connection() -> BlockingConnection:
        credentials = PlainCredentials(
            settings.RABBITMQ_DEFAULT_USER, settings.RABBITMQ_DEFAULT_PASS
        )
        parameters = ConnectionParameters(
            host=settings.RABBIT_HOST,
            port=settings.RABBIT_PORT,
            credentials=credentials,
        )
        try:
            connection = BlockingConnection(parameters)
        except AMQPError as e:
            base_logger.error(f"AMQP error during connection to rabbitMQ: {e}")
            raise e
        except Exception as e:
            base_logger.error(f"Unknown error during connection to rabbitMQ: {e}")
            raise e
        return connection

    def get_connection(self) -> BlockingConnection:
        if self.connection is None or self.connection.is_closed:
            self.connection = self.create_connection()
        return self.connection
