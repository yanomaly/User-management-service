from typing import Any, List, Optional

from domain.auth_schemas import KeyValuePair
from fastapi import HTTPException
from redis import Redis
from repository.queries.base import AbstractRepository, T


class AuthRepository(AbstractRepository[KeyValuePair]):

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def insert(self, value: KeyValuePair) -> KeyValuePair:
        try:
            self.redis.lpush(value.key, value.value.token)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return value

    def get_by_id(self, id: int | str) -> Optional[KeyValuePair]:
        try:
            user_tokens_blacklist = self.redis.lrange(id, 0, -1)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return KeyValuePair(key=id, value=user_tokens_blacklist)

    async def get_by(self, identifier_name: str, identifier: Any) -> Optional[T]:
        pass

    async def list(self, filters: dict) -> List[T]:
        pass

    async def update(self, record: T) -> T:
        pass

    async def delete(self, id: int | str) -> None:
        pass
