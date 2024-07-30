from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
import requests
from requests import Response

from app.shemas.error_list import ErrorParams
from app.shemas.user import User, Users
from tests.fixtures.database import connect, db_mydb  # noqa F401

if TYPE_CHECKING:
    from tests.fixtures.database import MyDB


@pytest.mark.usefixtures('prepare_table_users')
class TestsApi:
    def tests_users_no_duplicates(self, app_url: str):
        response: Response = requests.get(f"{app_url}/api/users/")
        users_ids = [user["id"] for user in response.json()['data']]
        assert len(users_ids) == len(set(users_ids))

    @pytest.mark.parametrize("user_id", [1, 6, 12])
    def test_user_id(self, app_url: str, user_id: int):
        response: Response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.OK
        User.model_validate(response.json())

    @pytest.mark.parametrize("user_id", [13])
    def test_user_nonexistent_values(self, app_url: str, user_id: int):
        response: Response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_user_invalid_values(self, app_url: str, user_id: int):
        response: Response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_users(self, app_url: str):
        response: Response = requests.get(f"{app_url}/api/users/")
        assert response.status_code == HTTPStatus.OK
        Users.model_validate(response.json())

    def test_update(self, app_url: str, db_mydb: 'MyDB'):
        response: Response = requests.patch(
            f"{app_url}/api/users/1",
            json={'first_name': '1234'}
        )
        assert response.status_code == HTTPStatus.OK
        User.model_validate(response.json())
        assert db_mydb.get_value('select first_name from users where id = 1')[0][0] == '1234'

    def test_update_not_cuh_user(self, app_url: str):
        response: Response = requests.patch(
            f"{app_url}/api/users/25",
            json={'first_name': '1234'}
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'detail': 'User not found'}

    def test_update_not_correct_payload(self, app_url: str):
        response: Response = requests.patch(
            f"{app_url}/api/users/1",
            json={'first_name': 1234}
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    def test_post(self, app_url: str, db_mydb: 'MyDB'):
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
        assert db_mydb.get_value(
            f'select first_name from users where id = {response.json()["id"]}',
        )[0][0] == "11111111morph2e56s"

    def test_post_not_correct_email(self, app_url: str):
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

    def test_post_not_correct_avatar(self, app_url: str):
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

    def test_delete(self, app_url: str, db_mydb: 'MyDB'):
        response: Response = requests.delete(
            f"{app_url}/api/users/1",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"message": "User deleted"}
        assert not len(db_mydb.get_value('select first_name from users where id = 1'))

    def test_delete_not_user(self, app_url: str, db_mydb: 'MyDB'):
        response: Response = requests.delete(
            f"{app_url}/api/users/21",
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {
            "detail": "User not found"
        }
        assert not len(db_mydb.get_value('select first_name from users where id = 21'))

    def test_delete_not_found(self, app_url: str, db_mydb: 'MyDB'):
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
        assert not len(db_mydb.get_value('select first_name from users where id = 2'))
