import re

import schemas
from pydantic import (
    BaseModel,
    SecretStr,
    ValidationInfo,
    field_validator,
    model_validator,
)
from schemas import UserBaseModel

password_regexp = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!_%*?&])[A-Za-z\d@$!_%*?&]{8,}$"
)


class SignUpForm(UserBaseModel):
    # password must contain at least eight characters,
    # at least one number and both lower and uppercase letters and special characters
    password: SecretStr
    password_repeat: SecretStr

    @field_validator("password")
    @classmethod
    def password_val(cls, value: SecretStr):
        password_pattern = re.compile(password_regexp)
        min_length = 8
        if len(value.get_secret_value()) < min_length:
            raise ValueError("This password format is not supported")
        if not re.match(password_pattern, value.get_secret_value()):
            raise ValueError("This password format is not supported")
        return value

    @model_validator(mode="after")
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


class LogInForm(BaseModel):
    identifier: str
    identifier_type: str = "id"
    password: SecretStr

    @field_validator("identifier_type")
    @classmethod
    def validate_one_field_using_the_others(cls, value: str, info: ValidationInfo):
        identifier = info.data["identifier"]

        phone_pattern = re.compile(schemas.phone_regexp)
        email_pattern = re.compile(schemas.email_regexp)
        username_pattern = re.compile(schemas.username_regexp)

        if re.match(phone_pattern, identifier):
            value = "phone_number"
        elif re.match(email_pattern, identifier):
            value = "email"
        elif re.match(username_pattern, identifier):
            value = "username"
        else:
            raise ValueError("Username, phone number or email isn't correct")

        return value
