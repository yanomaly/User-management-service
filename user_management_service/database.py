from config import Settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

settings = Settings()

engine = create_async_engine(
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
    echo=True,
)
session_factory = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()
