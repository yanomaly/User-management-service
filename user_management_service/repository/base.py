from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar, Union

from database import Base
from pydantic import BaseModel

T = TypeVar("T", bound=Union[Base, BaseModel])


class AbstractRepository(Generic[T], ABC):

    @abstractmethod
    async def get_by_id(self, id: int | str) -> Optional[T]: ...

    @abstractmethod
    async def get_by(self, identifier_name: str, identifier: Any) -> Optional[T]: ...

    @abstractmethod
    async def list(self, filters: dict) -> List[T]: ...

    @abstractmethod
    async def insert(self, record: T) -> T: ...

    @abstractmethod
    async def update(self, record: T) -> T: ...

    @abstractmethod
    async def delete(self, id: int | str) -> None: ...
