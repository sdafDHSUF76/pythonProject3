import json
import os
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
import requests
from requests import Response

from app.shemas.error_list import ErrorParams
from app.shemas.user import User, Users
from tests.utils import calculate_pages

if TYPE_CHECKING:
    from _pytest.python import Metafunc


def pytest_generate_tests(metafunc: 'Metafunc'):
    """Добавил параметризацию в тесты.

    Пришлось сделать ее динамической, так как тестовые данные, могут быть разного количества, но
    тут сильно не продумывал логику, сделал пока набросок, но суть здесь, в том, чтобы динамически
    подстраивать параметризацию от количества данных в users.json
    """
    with open(''.join((os.path.abspath(__file__).split('tests')[0], 'users.json'))) as f:
        users = json.load(f)
    if 'page_and_size_parametrize' in metafunc.fixturenames:
        # Generate test cases based on the user_roles list

        new_data_page_and_size = [
            (len(users) + 1, len(users), 0, len(users)),
            (len(users), len(users) + 1, 0, len(users)),
            (len(users) + 1, len(users) + 1, 0, len(users)),
            (1, 1, 1, len(users))
        ]
        metafunc.parametrize('page_and_size_parametrize', new_data_page_and_size)

    if 'data_page' in metafunc.fixturenames:
        new_data_page = [
            len(users) if len(users) > 1 else 1,
            1,
            99999999,
            2 if len(users) > 1 else 1,
        ]
        metafunc.parametrize('data_page', set(new_data_page))

    if 'data_size' in metafunc.fixturenames:
        new_data_size = [
            len(users) if len(users) > 1 else 1,
            1,
            2 if len(users) > 1 else 1,
        ]
        metafunc.parametrize('data_size', set(new_data_size))

    if 'different_page' in metafunc.fixturenames:
        new_data_page_and_size = [
            (1, 1, (users[0]['id'],)),
            (1, 2, (users[1]['id'],)),
            (2, 2, (users[2]['id'], users[3]['id'])),
            (2, 1, (users[0]['id'], users[1]['id'])),
            (3, 2, (users[3]['id'], users[4]['id'], users[5]['id'])),
            (5, 3, (users[10]['id'], users[11]['id'])),
        ]
        metafunc.parametrize('different_page', set(new_data_page_and_size))


def test_users_no_duplicates(app_url: str):
    response: Response = requests.get(f"{app_url}/api/users/")
    users_ids = [user["id"] for user in response.json()['items']]
    assert len(users_ids) == len(set(users_ids))


@pytest.mark.parametrize("user_id", [1, 6, 12])
def test_user_id(app_url: str, user_id: int):
    response: Response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.OK
    User.model_validate(response.json())


@pytest.mark.parametrize("user_id", [13])
def test_user_nonexistent_values(app_url: str, user_id: int):
    response: Response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_user_invalid_values(app_url: str, user_id: int):
    response: Response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "page, size",
    [
        (-1, -1),
        (999999, 999999),
        (0, 0),
        (1.5, 1.5),
        ('fafaf', 'fafaf'),
        ("@/*$%^&#*/()?>,.*/\"", "@/*$%^&#*/()?>,.*/\""),
        ('None', 'None'),
    ],
)
def test_users_invalid_page_and_size(app_url: str, page: int | str, size: int | str):
    response: Response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    ErrorParams.parse_obj(response.json())


def test_users_correct_values_page_and_size(
    app_url: str, page_and_size_parametrize: tuple[int, int, int, int],
):
    page, size, expected_count_user, total_users = page_and_size_parametrize
    response: Response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")
    assert response.status_code == HTTPStatus.OK
    response_payload: dict = Users.parse_obj(response.json()).dict()
    assert len(response_payload['items']) == expected_count_user
    assert response_payload['total'] == total_users
    assert response_payload['page'] == page
    assert response_payload['size'] == size
    assert response_payload['pages'] == calculate_pages(total_users, size)


def test_users_different_users_depending_on_page(
    app_url: str, different_page: tuple[int, int, tuple[int, ...]],
):
    size, page, expected_id_users = different_page
    response: Response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")
    assert response.status_code == HTTPStatus.OK
    response_payload: dict = Users.parse_obj(response.json()).dict()
    current_user_id = [
        unit['id'] for unit in response_payload['items'] if len(response_payload['items'])
    ]
    assert len(current_user_id) == len(expected_id_users), (
        'количество полученных юзеров не совпало с ожидаемым'
    )
    for id, user_id in enumerate(current_user_id):
        assert user_id == expected_id_users[id], (
            'Пришел не тут id user, что ожидали \n'
            f'current_user_id: {user_id}, expected_id_users: {expected_id_users[id]}'
        )


@pytest.mark.parametrize("page", [-1, 0, "fafaf", "@/*$%^&#*/()?>,.*/\"", 'None', 1.5])
def test_users_invalid_page(app_url: str, page: int | str | float):
    response: Response = requests.get(f"{app_url}/api/users/?page={page}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    ErrorParams.parse_obj(response.json())


@pytest.mark.parametrize("size", [-1, 0, "fafaf", "@/*$%^&#*/()?>,.*/\"", 99999999, 'None', 1.5])
def test_users_invalid_size(app_url: str, size: int | str | float):
    response: Response = requests.get(f"{app_url}/api/users/?size={size}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    ErrorParams.parse_obj(response.json())


def test_users_page(app_url: str, data_page: int):
    response: Response = requests.get(f"{app_url}/api/users/?page={data_page}")
    assert response.status_code == HTTPStatus.OK
    Users.parse_obj(response.json())


def test_users_size(app_url: str, data_size: int):
    response: Response = requests.get(f"{app_url}/api/users/?size={data_size}")
    assert response.status_code == HTTPStatus.OK
    Users.parse_obj(response.json())


def test_users(app_url: str):
    response: Response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    Users.parse_obj(response.json())
