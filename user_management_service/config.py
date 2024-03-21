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

    model_config = SettingsConfigDict(env_file=DOTENV)
