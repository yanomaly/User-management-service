import re

from pydantic import (
    BaseModel,
    SecretStr,
    ValidationInfo,
    field_validator,
    model_validator,
)

name_surname_regexp = r"^([А-Я][а-яё]{1,23}|[A-Z][a-z]{1,23})$"
username_regexp = r"[-_A-Za-z0-9]{1,19}$"
password_regexp = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!_%*?&])[A-Za-z\d@$!_%*?&]{8,}$"
email_regexp = r"^[\w.-]+@([\w-]+\.)+[\w-]{2,4}$"
phone_regexp = r"^(\+375)(29|25|44|33)(\d{7})$"


class SignUpForm(BaseModel):
    name: str
    surname: str
    username: str
    email: str
    phone_number: str
    # password must contain at least eight characters,
    # at least one number and both lower and uppercase letters and special characters
    password: SecretStr
    password_repeat: SecretStr

    @field_validator("name", "surname")
    @classmethod
    def name_surname_val(cls, value: str, info: ValidationInfo):
        name_surname_pattern = re.compile(name_surname_regexp)
        if not re.match(name_surname_pattern, value):
            raise ValueError(f"This {info.field_name} format is not supported")
        return value

    @field_validator("username")
    @classmethod
    def username_val(cls, value: str):
        username_pattern = re.compile(username_regexp)
        if not re.match(username_pattern, value):
            raise ValueError("This username format is not supported")
        return value

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

    @field_validator("email")
    @classmethod
    def email_val(cls, value: str):
        email_pattern = re.compile(email_regexp)
        if not re.match(email_pattern, value):
            raise ValueError("This email format is not supported")
        return value

    @field_validator("phone_number")
    @classmethod
    def phone_val(cls, value: str):
        phone_pattern = re.compile(phone_regexp)
        if not re.match(phone_pattern, value):
            raise ValueError("This phone format is not supported")
        return value


class LogInForm(BaseModel):
    identifier: str
    identifier_type: str
    password: SecretStr

    @field_validator("identifier_type")
    @classmethod
    def validate_one_field_using_the_others(cls, value: str, info: ValidationInfo):
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
