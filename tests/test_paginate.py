from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
import requests
from requests import Response
from sqlalchemy import create_engine

from app.shemas.error_list import ErrorParams
from app.shemas.user import Users
from tests.fixtures.database import DATABASE_URL  # noqa F401
from tests.fixtures.database import MyDB, connect  # noqa F401
from tests.utils import calculate_pages, fill_users_table

if TYPE_CHECKING:
    from _pytest.python import Metafunc


prepare_users = False
new_data_page_and_size: list


@pytest.mark.usefixtures('prepare_table_users')
class TestsPaginate:

    def pytest_generate_tests(self, metafunc: 'Metafunc'):
        """Добавил параметризацию в тесты.

        Пришлось сделать ее динамической, так как тестовые данные, могут быть разного количества, но
        тут сильно не продумывал логику, сделал пока набросок, но суть здесь, в том, чтобы
        динамически подстраивать параметризацию от количества данных в базе данных
        """
        global prepare_users
        global new_data_page_and_size
        global new_data_page
        global new_data_size
        global new_data_size_page_expected_page
        if not prepare_users:
            connect_db: MyDB = MyDB(
                create_engine(
                    DATABASE_URL,
                    # pool_size=os.getenv("DATABASE_POOL_SIZE", 10)
                ).connect(),
            )
            fill_users_table(connect_db)
            prepare_users = True
            count_users: int = connect_db.get_value('select count(id) from users')[0][0]
            users: list[dict] = connect_db.get_answer_in_form_of_dictionary('select * from users')
            new_data_page_and_size = [
                (count_users + 1, count_users, 0, count_users),
                (count_users, count_users + 1, 0, count_users),
                (count_users + 1, count_users + 1, 0, count_users),
                (1, 1, 1, count_users)
            ]
            new_data_page = [
                count_users if count_users > 1 else 1,
                1,
                2 if count_users > 1 else 1,
            ]
            new_data_size = [
                count_users if count_users > 1 else 1,
                1,
                2 if count_users > 1 else 1,
            ]
            new_data_size_page_expected_page = [
                (1, 1, (users[0]['id'],)),
                (1, 2, (users[1]['id'],)),
                (2, 2, (users[2]['id'], users[3]['id'])),
                (2, 1, (users[0]['id'], users[1]['id'])),
                (3, 2, (users[3]['id'], users[4]['id'], users[5]['id'])),
                (5, 3, (users[10]['id'], users[11]['id'])),
            ]
        if 'page_and_size_parametrize' in metafunc.fixturenames:
            metafunc.parametrize(
                'page_and_size_parametrize',
                new_data_page_and_size,
                ids=[
                    str(i)[1:-1].replace(', ', '-')
                    for i in new_data_page_and_size
                ]
            )

        if 'data_page' in metafunc.fixturenames:
            metafunc.parametrize(
                'data_page',
                set(new_data_page),
                ids=[
                    str(i)[1:-1].replace(', ', '-')
                    for i in set(new_data_page)
                ]
            )

        if 'data_size' in metafunc.fixturenames:
            metafunc.parametrize(
                'data_size',
                set(new_data_size),
                ids=[
                    str(i)[1:-1].replace(', ', '-')
                    for i in set(new_data_size)
                ]
            )

        if 'different_page' in metafunc.fixturenames:
            metafunc.parametrize(
                'different_page',
                set(new_data_size_page_expected_page),
                ids=[
                    str(i)[1:-1].replace(', ', '-', 2)
                    for i in set(new_data_size_page_expected_page)
                ]
            )

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
    def test_users_invalid_page_and_size(self, app_url: str, page: int | str, size: int | str):
        response: Response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    def test_users_correct_values_page_and_size(
        self, app_url: str, page_and_size_parametrize: tuple[int, int, int, int],
    ):
        page, size, expected_count_user, total_users = page_and_size_parametrize
        response: Response = requests.get(f"{app_url}/api/users/?page={page}&per_page={size}")
        assert response.status_code == HTTPStatus.OK
        response_payload: dict = Users.model_validate(response.json()).model_dump()
        assert len(response_payload['data']) == expected_count_user
        assert response_payload['total'] == total_users
        assert response_payload['page'] == page
        assert response_payload['per_page'] == size
        assert response_payload['total_pages'] == calculate_pages(total_users, size)

    def test_users_different_users_depending_on_page(
        self, app_url: str, different_page: tuple[int, int, tuple[int, ...]],
    ):
        size, page, expected_id_users = different_page
        response: Response = requests.get(f"{app_url}/api/users/?page={page}&per_page={size}")
        assert response.status_code == HTTPStatus.OK
        response_payload: dict = Users.model_validate(response.json()).model_dump()
        current_user_id = [
            unit['id'] for unit in response_payload['data'] if len(response_payload['data'])
        ]
        assert len(current_user_id) == len(expected_id_users), (
            'количество полученных юзеров не совпало с ожидаемым'
        )
        for id, user_id in enumerate(current_user_id):
            assert user_id == expected_id_users[id], (
                'Пришел не тут id user, что ожидали \n'
                f'current_user_id: {user_id}, expected_id_users: {expected_id_users[id]}'
            )

    @pytest.mark.parametrize(
        "page", [-1, 0, "fafaf", "@/*$%^&#*/()?>,.*/\"", 99999999, 'None', 1.5],
    )
    def test_users_invalid_page(self, app_url: str, page: int | str | float):
        response: Response = requests.get(f"{app_url}/api/users/?page={page}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    @pytest.mark.parametrize(
        "size", [-1, 0, "fafaf", "@/*$%^&#*/()?>,.*/\"", 99999999, 'None', 1.5],
    )
    def test_users_invalid_size(self, app_url: str, size: int | str | float):
        response: Response = requests.get(f"{app_url}/api/users/?per_page={size}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    def test_users_page(self, app_url: str, data_page: int):
        response: Response = requests.get(f"{app_url}/api/users/?page={data_page}")
        assert response.status_code == HTTPStatus.OK
        Users.model_validate(response.json())

    def test_users_size(self, app_url: str, data_size: int):
        response: Response = requests.get(f"{app_url}/api/users/?per_page={data_size}")
        assert response.status_code == HTTPStatus.OK
        Users.model_validate(response.json())
