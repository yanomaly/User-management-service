from typing import Optional

from schemas import UserBaseModel
from users.model import Role


class UpdateForm(UserBaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[Role] = None
    group_id: Optional[str] = None
    image: Optional[str] = None
    is_blocked: Optional[bool] = None
