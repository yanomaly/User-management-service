import re
from enum import Enum
from typing import Annotated, Any, Optional

from domain.base import UserBaseModel, email_regexp, phone_regexp, username_regexp
from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo

password_regexp = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!_%*?&])[A-Za-z\d@$!_%*?&]{8,}$"
)
token_regexp = r"(^[\w=-]{32,}\.[\w=-]{32,}\.[\w=-]{32,}$)"


def password_val(value: SecretStr):
    password_pattern = re.compile(password_regexp)
    min_length = 8
    if len(value.get_secret_value()) < min_length:
        raise ValueError("This password format is not supported")
    if not re.match(password_pattern, value.get_secret_value()):
        raise ValueError("This password format is not supported")
    return value


def check_passwords_match(self):
    password = self.password
    password_repeat = self.password_repeat
    if (
        password is not None
        and password_repeat is not None
        and password.get_secret_value() != password_repeat.get_secret_value()
    ):
        raise ValueError("Passwords do not match")
    return self


def define_identifier_type(cls, value: str, info: ValidationInfo):
    identifier = info.data["identifier"]

    phone_pattern = re.compile(phone_regexp)
    email_pattern = re.compile(email_regexp)
    username_pattern = re.compile(username_regexp)

    if re.match(phone_pattern, identifier):
        value = "phone_number"
    elif re.match(email_pattern, identifier):
        value = "email"
    elif re.match(username_pattern, identifier):
        value = "username"
    else:
        raise ValueError("Username, phone number or email isn't correct")

    return value


class SignUpForm(UserBaseModel):
    # password must contain at least eight characters,
    # at least one number and both lower and uppercase letters and special characters
    password: SecretStr
    password_repeat: SecretStr

    validate_pass = field_validator("password")(password_val)
    validate_repeat = model_validator(mode="after")(check_passwords_match)


class LogInForm(BaseModel):
    identifier: str
    identifier_type: Annotated[Optional[str], Field(validate_default=True)] = None
    password: SecretStr

    validate_identifier = field_validator("identifier_type")(define_identifier_type)


class TokenTypeEnum(Enum):
    access = "access"
    refresh = "refresh"
    reset = "reset"


class JwtTokenForm(BaseModel):
    token: str
    type: TokenTypeEnum

    @field_validator("token")
    @classmethod
    def token_val(cls, value: str):
        token_pattern = re.compile(token_regexp)
        if not re.match(token_pattern, value):
            raise ValueError("Invalid token")
        return value


class KeyValuePair(BaseModel):
    key: int | str
    value: Optional[Any]


class ResetPassword(BaseModel):
    password: SecretStr
    password_repeat: SecretStr

    validate_pass = field_validator("password", check_fields=False)(password_val)
    validate_repeat = model_validator(mode="after")(check_passwords_match)


class ForgetForm(BaseModel):
    identifier: str
    identifier_type: Annotated[Optional[str], Field(validate_default=True)] = None

    validate_identifier = field_validator("identifier_type")(define_identifier_type)
