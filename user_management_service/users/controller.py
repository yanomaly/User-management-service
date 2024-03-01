import datetime

from fastapi import HTTPException
from pagination import paginate
from schemas import Pagination
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from users.model import User
from users.schemas import UpdateForm


async def find_user_db(identifier_type: str, identifier: str, session: AsyncSession):
    query = select(User).where(getattr(User, identifier_type) == identifier)
    return (await session.execute(query)).scalars().first()


async def update_user_db(user: User, new_data: UpdateForm, session: AsyncSession):
    update_attributes = delete_none_from_list(new_data)
    update_attributes.update({"modified_at": datetime.datetime.utcnow()})
    query = (
        update(User).where(User.id == user.id).values(update_attributes).returning(User)
    )
    updated_user = (await session.execute(query)).scalars().first()
    if not updated_user:
        raise HTTPException(status_code=404, detail="User doesn't exist")
    await session.commit()
    return updated_user


def delete_none_from_list(new_data: UpdateForm):
    return {k: v for k, v in new_data.dict().items() if v is not None}


async def delete_user_db(user_id: str, session: AsyncSession):
    query = delete(User).where(User.id == user_id).returning(User.id)
    deleted_user = (await session.execute(query)).scalars().first()
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User doesn't exist")
    await session.commit()
    return deleted_user


def if_group_admin_or_moderator(user: User, group_id: str):
    return if_group_admin(user, group_id) or if_group_moderator(user, group_id)


def if_group_admin(user: User, group_id: str):
    return if_in_group(user, group_id) and if_admin(user)


def if_group_moderator(user: User, group_id: str):
    return if_in_group(user, group_id) and if_moderator(user)


def if_in_group(user: User, group_id: str):
    return user and group_id and user.group_id == group_id


def if_admin(user: User):
    return user and user.role.value == "admin"


def if_moderator(user: User):
    return user and user.role.value == "moderator"


async def paginate_users(
    user: User, pagination_params: Pagination, session: AsyncSession
):
    if if_admin(user):
        return await paginate(
            User,
            session,
            pagination_params,
            {"surname": pagination_params.filter_by_surname},
        )
    elif if_moderator(user):
        return await paginate(
            User,
            session,
            pagination_params,
            {"group_id": user.group_id, "surname": pagination_params.filter_by_surname},
        )
    else:
        raise HTTPException(status_code=403, detail="You aren't an admin or moderator")
