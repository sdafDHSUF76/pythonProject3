from typing import Optional

from pydantic import BaseModel, EmailStr, Extra, HttpUrl


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
    items: list[Optional[User]]
    total: int
    page: int
    size: int
    pages: int
