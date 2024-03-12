from datetime import datetime
from typing import List, Optional

from dependencies import get_session
from domain.user_schemas import UpdateForm
from fastapi import Depends, HTTPException
from models.user_models import User
from repository.base import AbstractRepository, T
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class UsersRepository(AbstractRepository[User]):

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def insert(self, user: User) -> Optional[User]:
        try:
            self.session.add(user)
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(status_code=400, detail="User already exists")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return user

    async def get_by(self, identifier: str, identifier_type: str) -> Optional[User]:
        try:
            query = select(User).where(getattr(User, identifier_type) == identifier)
            query_result = await self.session.execute(query)
            user_to_return = query_result.scalars().first()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return user_to_return

    async def update(self, user: User) -> Optional[User]:
        try:
            fields_to_update = UpdateForm(**dict(user.__dict__)).dict()
            fields_to_update.update({"modified_at": datetime.utcnow()})
            query = (
                update(User)
                .where(User.id == user.id)
                .values(fields_to_update)
                .returning(User)
            )
            query_result = await self.session.execute(query)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return query_result.scalars().first()

    async def delete(self, user_id: str) -> Optional[User]:
        try:
            query = delete(User).where(User.id == user_id).returning(User)
            query_result = await self.session.execute(query)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return query_result.scalars().first()

    async def get_by_id(self, id: int | str) -> Optional[T]:
        return await self.get_by(id, "id")

    async def list(self, filters: dict) -> List[T]:
        pass
