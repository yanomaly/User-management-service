import re
from enum import Enum

from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

name_surname_regexp = r"^[A-Z][a-z]{1,23}$"
username_regexp = r"[-_A-Za-z0-9]{1,19}$"
email_regexp = r"^[\w.-]+@([\w-]+\.)+[\w-]{2,4}$"
phone_regexp = r"^(\+375)(29|25|44|33)(\d{7})$"


class UserBaseModel(BaseModel):
    name: str
    surname: str
    username: str
    email: str
    phone_number: str

    @field_validator("name", "surname")
    @classmethod
    def name_surname_val(cls, value: str, info: ValidationInfo):
        name_surname_pattern = re.compile(name_surname_regexp)
        if not value or not re.match(name_surname_pattern, value):
            raise ValueError(f"This {info.field_name} format is not supported")
        return value

    @field_validator("username")
    @classmethod
    def username_val(cls, value: str):
        username_pattern = re.compile(username_regexp)
        if not value or not re.match(username_pattern, value):
            raise ValueError("This username format is not supported")
        return value

    @field_validator("email")
    @classmethod
    def email_val(cls, value: str):
        email_pattern = re.compile(email_regexp)
        if not value or not re.match(email_pattern, value):
            raise ValueError("This email format is not supported")
        return value

    @field_validator("phone_number")
    @classmethod
    def phone_val(cls, value: str):
        phone_pattern = re.compile(phone_regexp)
        if not value or not re.match(phone_pattern, value):
            raise ValueError("This phone format is not supported")
        return value


class OrderEnum(Enum):
    ASC = "asc"
    DESC = "desc"


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1, le=500000)
    per_page: int = Field(default=2, ge=1, le=1000)
    filter_by_surname: str
    order: OrderEnum = OrderEnum.DESC
    order_by: str = "id"
