import os

import aioboto3
import redis
from botocore.client import BaseClient
from domain.auth_schemas import JwtTokenForm
from fastapi.security import HTTPBearer
from models.user_models import Group, Role, User
from passlib.context import CryptContext
from pika.adapters.blocking_connection import BlockingConnection
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials
from pika.exceptions import AMQPError
from redis import Redis
from service.tokens import encode_tokens
from sqlalchemy import NullPool

os.chdir("user_management_service")

from typing import AsyncGenerator

import pytest
from config import SettingsTest
from database import Base
from dependencies import (
    RabbitMQClient,
    base_logger,
    get_redis_client,
    get_s3_client,
    get_session,
    http_bearer,
)
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from user_management_service.main import app

settings_test = SettingsTest()


override_http_bearer = HTTPBearer()


DATABASE_URL_TEST = (
    f"postgresql+asyncpg://{settings_test.POSTGRES_USER}:{settings_test.POSTGRES_PASSWORD}"
    f"@{settings_test.POSTGRES_HOST}:{settings_test.POSTGRES_PORT}/{settings_test.POSTGRES_DB}"
)


engine_test = create_async_engine(DATABASE_URL_TEST, echo=True, poolclass=NullPool)
session_factory_test = async_sessionmaker(
    bind=engine_test, expire_on_commit=False, class_=AsyncSession
)


redis_client = redis.Redis(
    host=settings_test.REDIS_HOST, port=settings_test.REDIS_PORT, decode_responses=True
)


aws_session = aioboto3.Session()


async def override_get_async_session() -> AsyncSession:
    async with session_factory_test() as session:
        yield session


def override_get_redis_client() -> Redis:
    return redis_client


async def override_get_s3_client() -> BaseClient:
    async with aws_session.client(
        service_name="s3",
        region_name=settings_test.DEFAULT_REGION,
        aws_access_key_id=settings_test.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings_test.AWS_SECRET_ACCESS_KEY,
        endpoint_url=f"http://{settings_test.HOSTNAME_EXTERNAL}:{settings_test.LOCALSTACK_PORT}",
    ) as client_s3:
        yield client_s3


class OverrideRabbitMQClient:
    def __init__(self):
        self.connection = self.create_connection()

    @staticmethod
    def create_connection() -> BlockingConnection:
        credentials = PlainCredentials(
            settings_test.RABBITMQ_DEFAULT_USER, settings_test.RABBITMQ_DEFAULT_PASS
        )
        parameters = ConnectionParameters(
            host=settings_test.RABBIT_HOST,
            port=settings_test.RABBIT_PORT,
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


app.dependency_overrides[get_session] = override_get_async_session
app.dependency_overrides[get_redis_client] = override_get_redis_client
app.dependency_overrides[get_s3_client] = override_get_s3_client
app.dependency_overrides[http_bearer] = override_http_bearer
app.dependency_overrides[RabbitMQClient] = OverrideRabbitMQClient


@pytest.fixture(scope="session")
def validation_id() -> str:
    return "1276bb90-9923-4658-85e7-b708c93dd23b"


@pytest.fixture(autouse=True, scope="session")
async def prepare_database(validation_id) -> None:
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await fill_db(validation_id)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def fill_db(validation_id) -> None:
    async with session_factory_test() as session:
        group = Group(name="test")
        admin = User(
            name="Admin",
            surname="Admin",
            username="admin",
            password=CryptContext(schemes=["bcrypt"], deprecated="auto").hash(
                "Test19Test_"
            ),
            email="admin@gmail.com",
            phone_number="+375291111111",
            role=Role.ADMIN,
        )
        moderator = User(
            id=validation_id,
            name="Moder",
            surname="Moder",
            username="moder",
            password=CryptContext(schemes=["bcrypt"], deprecated="auto").hash(
                "Test19Test_"
            ),
            email="moder@gmail.com",
            phone_number="+375292222222",
            role=Role.MODERATOR,
            group=group,
        )
        blocked = User(
            name="Block",
            surname="Ban",
            username="blocked",
            password=CryptContext(schemes=["bcrypt"], deprecated="auto").hash(
                "Test19Test_"
            ),
            email="blocked@gmail.com",
            phone_number="+375293333333",
            role=Role.USER,
            is_blocked=True,
            group=group,
        )
        session.add_all([group, admin, moderator, blocked])
        await session.commit()


@pytest.fixture(scope="session")
async def valid_tokens(validation_id) -> list[JwtTokenForm]:
    return encode_tokens(validation_id)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
