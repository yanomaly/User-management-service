from datetime import datetime
from typing import Optional
from uuid import UUID

from domain.base import UserBaseModel
from repository.models.user_models import Role


class UpdateForm(UserBaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[Role] = None
    group_id: Optional[UUID] = None
    image: Optional[str] = None
    is_blocked: Optional[bool] = None


class UserReturnForm(UserBaseModel):
    id: UUID
    role: Role
    group_id: Optional[UUID]
    image: Optional[str]
    is_blocked: bool
    created_at: datetime
    modified_at: datetime
