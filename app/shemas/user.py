from typing import Optional, Iterable, Type

import re
from pydantic import BaseModel, EmailStr, Extra, HttpUrl, field_validator


class User(BaseModel, extra=Extra.forbid):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    avatar: HttpUrl


class Users(BaseModel, extra=Extra.forbid):
    """Из-за особенности пагинации, что используем в ендпоинте тут модель выглядит не как оригинал.

    Посмотрел по коду, как менять модель в пагинации и там на первый взгляд это не так просто
    окозалось, поэтому решил пока так оставить. Чтобы было ясно, там нужно в класс пагинации что-то
    переназначить/указывать, чтобы он иначе обрабатывал пагинацию
    """
    data: list | list[User]
    total: int
    page: int
    per_page: int
    total_pages: int


class UserCreate(BaseModel, extra=Extra.forbid):
    email: EmailStr
    first_name: str
    last_name: str
    avatar: str # TODO сделать валидацию HttpUrl через метод, суть в том, что база данных не поддерживает такой тип данных


    # Define a validator for the email field
    @field_validator("avatar")
    def check_email(cls, value):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        # assert re.match(regex, value) is not None  # True
        # print(re.match(regex, "example.com") is not None)  # False

        # use a regex to check that the email has a valid format
        # email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(regex, value):
            raise ValueError("Invalid email address")
        return value


class UserUpdate(BaseModel, extra=Extra.forbid):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar: HttpUrl | None = None
