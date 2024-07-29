import re

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl, field_validator


class User(BaseModel):

    model_config = ConfigDict(extra='forbid')

    id: int
    email: EmailStr
    first_name: str
    last_name: str
    avatar: HttpUrl


class Users(BaseModel):

    model_config = ConfigDict(extra='forbid')

    data: list | list[User]
    total: int
    page: int
    per_page: int
    total_pages: int


class UserCreate(BaseModel):

    model_config = ConfigDict(extra='forbid')

    email: EmailStr
    first_name: str
    last_name: str
    avatar: str

    @field_validator("avatar")
    def check_email(cls, value):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...  # noqa E501
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not re.match(regex, value):
            raise ValueError("Invalid email address")
        return value


class UserCreateResponse(BaseModel):

    model_config = ConfigDict(extra='forbid')

    name: str
    job: str
    id: str
    createdAt: str


class UserDeleteResponse(BaseModel):

    model_config = ConfigDict(extra='forbid')

    message: str


class UserUpdate(BaseModel):

    model_config = ConfigDict(extra='forbid')

    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar: HttpUrl | None = None
