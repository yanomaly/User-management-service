import os

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), ".env")


class Settings(BaseSettings):
    REDIS_USER: str
    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRATION_MINUTES: int
    REFRESH_TOKEN_EXPIRATION_MINUTES: int
    RESET_TOKEN_EXPIRATION_MINUTES: int
    APP_HOST: str
    APP_PORT: int
      
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBIT_HOST: str
    RABBIT_PORT: int
    ROUTING_KEY: str

    SERVICES: str
    HOSTNAME: str
    LOCALSTACK_PORT: int
    HOSTNAME_EXTERNAL: str
    DEFAULT_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    BUCKET_NAME: str
    PRESIGNED_URL_EXPIRATION_SECONDS: int

    model_config = SettingsConfigDict(env_file=DOTENV)
