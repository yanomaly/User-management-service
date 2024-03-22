import logging

import redis
from config import Settings
from database import session_factory
from fastapi.security import HTTPBearer
from pika.adapters.blocking_connection import BlockingConnection
from pika.channel import Channel
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials
from pika.exceptions import AMQPError

logging.config.fileConfig("../logger.ini")
auth_logger = logging.getLogger("auth")
users_logger = logging.getLogger("users")
base_logger = logging.getLogger("base")

settings = Settings()

http_bearer = HTTPBearer()

redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
)


def get_redis_client():
    return redis_client


async def get_session():
    async with session_factory() as session:
        yield session


class RabbitMQClient:
    def __init__(self):
        self.connection = self.create_connection()

    @staticmethod
    def create_connection() -> BlockingConnection:
        credentials = PlainCredentials(
            settings.RABBITMQ_DEFAULT_USER, settings.RABBITMQ_DEFAULT_PASS
        )
        parameters = ConnectionParameters(
            host=settings.RABBIT_HOST, credentials=credentials
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

    def get_channel(self) -> Channel:
        if self.connection is None or self.connection.is_closed:
            self.connection = self.create_connection()
        with self.connection.channel() as channel:
            yield channel


rabbit_client = RabbitMQClient()
