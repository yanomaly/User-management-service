from typing import Any, List, Optional

from dependencies import auth_logger, get_redis_client
from domain.auth_schemas import KeyValuePair
from fastapi import Depends
from redis import Redis, RedisError
from repository.base import AbstractRepository, T


class AuthRepository(AbstractRepository[KeyValuePair]):

    def __init__(self, redis: Redis = Depends(get_redis_client)) -> None:
        self.redis = redis

    def insert(self, value: KeyValuePair) -> KeyValuePair:
        try:
            self.redis.lpush(value.key, value.value.token)
        except RedisError as e:
            auth_logger.error(f"Redis error during insertion: {e}", exc_info=True)
            raise e
        except Exception as e:
            auth_logger.error(f"Unknown error during insertion: {e}", exc_info=True)
            raise e
        return value

    def get_by_id(self, id: int | str) -> Optional[KeyValuePair]:
        try:
            user_tokens_blacklist = self.redis.lrange(id, 0, -1)
            value_to_return = KeyValuePair(key=id, value=user_tokens_blacklist)
        except RedisError as e:
            auth_logger.error(f"Redis error during getting value: {e}", exc_info=True)
            raise e
        except Exception as e:
            auth_logger.error(f"Unknown error during getting value: {e}", exc_info=True)
            raise e
        return value_to_return

    async def get_by(self, identifier_name: str, identifier: Any) -> Optional[T]:
        pass

    async def list(self, filters: dict) -> List[T]:
        pass

    async def update(self, record: T) -> T:
        pass

    async def delete(self, id: int | str) -> None:
        pass
