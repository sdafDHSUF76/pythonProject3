from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.database import users_db
from app.shemas.user import (
    User,
    UserCreate,
    UserCreateResponse,
    UserDeleteResponse,
    Users,
    UserUpdate,
)

router = APIRouter(prefix="/api/users")


def _calculate_total_pages(total_users: int, per_page: int) -> int:
    """Вычисляем общее количество страниц."""
    return (total_users + per_page - 1) // per_page


def _get_start_and_end_index(page: int, per_page: int) -> (int, int):
    """Вычисляем начальный и конечный индекс для извлечения данные.

    По указанным page, per_page получаем нужные данные из users_data.
    """
    start_index: int = (page - 1) * per_page
    end_index: int = start_index + per_page
    return start_index, end_index


def _get_users_on_page(
    page: int, per_page: int, total_pages: int, users_data: list[User],
) -> list | list[dict]:
    """Получаем данные сущностей на странице по нашим page, и total_pages.

    Если page > общего количества страниц, то возвращаем [], если указанная страница входит в общее
    количество страниц, то выдаем данные по этой странице.
    """
    if page > total_pages:
        return []
    else:
        # Вычисляем индекс начала и конца для текущей страницы
        start_index, end_index = _get_start_and_end_index(page, per_page)
        return users_data[start_index:end_index]


@router.get("/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    user: Optional[User] = users_db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


@router.get("/", status_code=HTTPStatus.OK)
def get_users(
    page: Optional[int] = Query(None, ge=1, le=100, description="Page number"),
    per_page: Optional[int] = Query(None, ge=1, le=100, description="number of entities per page")
) -> Users:
    users_data: list[User] = users_db.get_users()
    default_per_page = 6
    default_number_page = 1
    total_users = len(users_data)
    per_page: int = per_page if per_page else default_per_page
    page: int = page if page else default_number_page
    total_pages: int = _calculate_total_pages(total_users, per_page)
    users_on_page = _get_users_on_page(page, per_page, total_pages, users_data)
    return Users(**{
        'data': users_on_page,
        'total': total_users,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
    })


@router.post("/", status_code=HTTPStatus.CREATED)
def create_user(user: UserCreate) -> UserCreateResponse:
    UserCreate.model_validate(user.model_dump())
    return users_db.create_user(user)


@router.patch("/{user_id}", status_code=HTTPStatus.OK)
def update_user(user_id: int, payload: UserUpdate) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    return users_db.update_user(user_id, payload)


@router.delete("/{user_id}", status_code=HTTPStatus.OK)
def delete_user(user_id: int) -> UserDeleteResponse:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    users_db.delete_user(user_id)
    return UserDeleteResponse(**{"message": "User deleted"})
