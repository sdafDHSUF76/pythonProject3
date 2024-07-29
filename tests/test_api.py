import json
import os
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
import requests
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from requests import Response
import psycopg2

from app.shemas.error_list import ErrorParams
from app.shemas.user import User, Users
from tests.fixtures.database import MyDB, db_mydb, connect
from tests.utils import calculate_pages

if TYPE_CHECKING:
    from _pytest.python import Metafunc
    from _pytest.main import Session

prepare_users = False
# new_data_page_and_size: list

# @pytest.fixture(scope='class')
def prepare_table_users(connect_postgres: MyDB) -> None:
    connect_postgres.execute(
        'TRUNCATE users;\n'
        'ALTER SEQUENCE users_id_seq RESTART WITH 1;\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'george.bluth@reqres.in', 'George', 'Bluth', 'https://reqres.in/img/faces/1-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'anet.weaver@reqres.in', 'Janet', 'Weaver', 'https://reqres.in/img/faces/2-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'emma.wong@reqres.in', 'Emma', 'Wong', 'https://reqres.in/img/faces/3-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'eve.holt@reqres.in', 'Eve', 'Holt', 'https://reqres.in/img/faces/4-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'charles.morris@reqres.in', 'Charles', 'Morris', 'https://reqres.in/img/faces/5-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'tracey.ramos@reqres.in', 'Tracey', 'Ramos', 'https://reqres.in/img/faces/6-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'michael.lawson@reqres.in', 'Michael', 'Lawson', 'https://reqres.in/img/faces/7-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'lindsay.ferguson@reqres.in', 'Lindsay', 'Ferguson',"
        " 'https://reqres.in/img/faces/8-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'tobias.funke@reqres.in', 'Tobias', 'Funke', 'https://reqres.in/img/faces/9-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'byron.fields@reqres.in', 'Byron', 'Fields', 'https://reqres.in/img/faces/10-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'george.edwards@reqres.in', 'George', 'Edwards',"
        " 'https://reqres.in/img/faces/11-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'rachel.howell@reqres.in', 'Rachel', 'Howell', 'https://reqres.in/img/faces/12-image.jpg'"
        ');\n'
    )


# @pytest.fixture(scope='class')
def pytest_generate_tests(metafunc: 'Metafunc'):
    """Добавил параметризацию в тесты.

    Пришлось сделать ее динамической, так как тестовые данные, могут быть разного количества, но
    тут сильно не продумывал логику, сделал пока набросок, но суть здесь, в том, чтобы динамически
    подстраивать параметризацию от количества данных в users.json
    """
    global prepare_users
    global new_data_page_and_size
    global new_data_page
    global new_data_size
    global new_data_size_page_expected_page
    if not prepare_users:
        connect_db: MyDB = MyDB(psycopg2.connect(
                dbname='mydb',
                user='myuser',
                password='mypassword',
                host='127.0.0.1',
                port='5436',
        ))
        prepare_table_users(connect_db)
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
    # a: psycopg2._psycopg.connection = psycopg2.connect(
    #         dbname='mydb',
    #         user='myuser',
    #         password='mypassword',
    #         host='127.0.0.1',
    #         port='5436',
    # )
    # a.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    # cursor = a.cursor()
    #
    # pass
    # cursor.execute('select id from users where id = 1')
    # # c = a.commit().fetchall()
    # c = cursor.fetchall()
    # with open(''.join((os.path.abspath(__file__).split('api')[0], 'users.json'))) as f:
    #     users = json.load(f)
    if 'page_and_size_parametrize' in metafunc.fixturenames:
        # Generate test cases based on the user_roles list
        metafunc.parametrize('page_and_size_parametrize', new_data_page_and_size)

    if 'data_page' in metafunc.fixturenames:
        metafunc.parametrize('data_page', set(new_data_page))

    if 'data_size' in metafunc.fixturenames:
        metafunc.parametrize('data_size', set(new_data_size))

    if 'different_page' in metafunc.fixturenames:
        metafunc.parametrize('different_page', set(new_data_size_page_expected_page))




# @pytest.mark.usefixtures('prepare_table_users')
# class TestApi:


def test_users_no_duplicates(app_url: str):
    response: Response = requests.get(f"{app_url}/api/users/")
    users_ids = [user["id"] for user in response.json()['data']]
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
    ErrorParams.model_validate(response.json())


def test_users_correct_values_page_and_size(
    app_url: str, page_and_size_parametrize: tuple[int, int, int, int],
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
    app_url: str, different_page: tuple[int, int, tuple[int, ...]],
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


@pytest.mark.parametrize("page", [-1, 0, "fafaf", "@/*$%^&#*/()?>,.*/\"", 99999999, 'None', 1.5])
def test_users_invalid_page(app_url: str, page: int | str | float):
    response: Response = requests.get(f"{app_url}/api/users/?page={page}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    ErrorParams.model_validate(response.json())


@pytest.mark.parametrize("size", [-1, 0, "fafaf", "@/*$%^&#*/()?>,.*/\"", 99999999, 'None', 1.5])
def test_users_invalid_size(app_url: str, size: int | str | float):
    response: Response = requests.get(f"{app_url}/api/users/?per_page={size}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    ErrorParams.model_validate(response.json())


def test_users_page(app_url: str, data_page: int):
    response: Response = requests.get(f"{app_url}/api/users/?page={data_page}")
    assert response.status_code == HTTPStatus.OK
    Users.model_validate(response.json())


def test_users_size(app_url: str, data_size: int):
    response: Response = requests.get(f"{app_url}/api/users/?per_page={data_size}")
    assert response.status_code == HTTPStatus.OK
    Users.model_validate(response.json())


def test_users(app_url: str):
    response: Response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    Users.model_validate(response.json())


def test_update(app_url: str, db_mydb: MyDB):
    response: Response = requests.patch(
        f"{app_url}/api/users/1",
        json={'first_name': '1234'}
    )
    assert response.status_code == HTTPStatus.OK
    User.model_validate(response.json())
    assert db_mydb.get_value('select first_name from users where id = 1')[0][0] == '1234'


def test_update_not_cuh_user(app_url: str):
    response: Response = requests.patch(
        f"{app_url}/api/users/25",
        json={'first_name': '1234'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    # User.parse_obj(response.json())
    assert response.json() == {'detail': 'User not found'}

def test_update_not_correct_payload(app_url: str):
    response: Response = requests.patch(
        f"{app_url}/api/users/1",
        json={'first_name': 1234}
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    ErrorParams.model_validate(response.json())
    # assert response.json() == {'detail': 'User not found'}


def test_post(app_url: str, db_mydb: MyDB):
    response: Response = requests.post(
        f"{app_url}/api/users/",
        json={
    "email": "george.bluth@reqres.in",
    "first_name": "11111111morph2e56s",
    "last_name": "Bluth",
    "avatar": "https://reqres.in/img/faces/1-image.jpg"
}
    )
    assert response.status_code == HTTPStatus.CREATED
    # response_payload: dict = User.parse_obj().dict()
    assert db_mydb.get_value(f'select first_name from users where id = {response.json()["id"]}')[0][0] == "11111111morph2e56s"

def test_post_not_correct_email(app_url: str):
    response: Response = requests.post(
        f"{app_url}/api/users/",
        json={
    "email": "george.bluthreqres.in",
    "first_name": "11111111morph2e56s",
    "last_name": "Bluth",
    "avatar": "https://reqres.in/img/faces/1-image.jpg"
}
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    ErrorParams.model_validate(response.json())

def test_post_not_correct_avatar(app_url: str):
    response: Response = requests.post(
        f"{app_url}/api/users/",
        json={
    "email": "george.bluth@reqres.in",
    "first_name": "11111111morph2e56s",
    "last_name": "Bluth",
    "avatar": "//reqres.in/img/faces/1-image.jpg"
}
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    ErrorParams.model_validate(response.json())


def test_delete(app_url: str, db_mydb: MyDB):
    response: Response = requests.delete(
        f"{app_url}/api/users/1",
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}
    # response_payload: dict = User.parse_obj().dict()
    assert not len(db_mydb.get_value('select first_name from users where id = 1'))

def test_delete_not_user(app_url: str, db_mydb: MyDB):
    response: Response = requests.delete(
        f"{app_url}/api/users/21",
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "detail": "User not found"
    }
    # response_payload: dict = User.parse_obj().dict()
    assert not len(db_mydb.get_value('select first_name from users where id = 21'))

def test_delete_not_found(app_url: str, db_mydb: MyDB):
    requests.delete(
        f"{app_url}/api/users/2",
    )
    response: Response = requests.delete(
        f"{app_url}/api/users/2",
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "detail": "User not found"
    }
    # response_payload: dict = User.parse_obj().dict()
    assert not len(db_mydb.get_value('select first_name from users where id = 2'))