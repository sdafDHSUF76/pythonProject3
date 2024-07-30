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

    def test_update_one_field_payload(self, app_url: str, db_mydb: 'MyDB'):
        response: Response = requests.patch(
            f"{app_url}/api/users/1",
            json={'first_name': '1234'}
        )
        assert response.status_code == HTTPStatus.OK
        User.model_validate(response.json())
        assert db_mydb.get_value('select first_name from users where id = 1')[0][0] == '1234'

    def test_update_all_fields(self, app_url: str, db_mydb: 'MyDB'):
        payload_template = {
            "email": "george.bluth@reqres.in",
            "first_name": "11111111morph2e56s",
            "last_name": "Bluth",
            "avatar": "http://reqres.in/img/faces/1-image.jpg"
        }
        response: Response = requests.patch(
            f"{app_url}/api/users/1",
            json=payload_template
        )
        assert response.status_code == HTTPStatus.OK
        User.model_validate(response.json())
        assert db_mydb.get_answer_in_form_of_dictionary(
            'select email, first_name, last_name, avatar from users where id = 1'
        )[0] == payload_template

    def test_update_non_existent_user(self, app_url: str, db_mydb: 'MyDB'):
        non_existent_user_id: int = db_mydb.get_value(
            'select id from users order by id desc'
        )[0][0] + 1
        response: Response = requests.patch(
            f"{app_url}/api/users/{non_existent_user_id}",
            json={'first_name': '1234'}
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'detail': 'User not found'}

    def test_update_without_payload(self, app_url: str):
        response: Response = requests.patch(
            f"{app_url}/api/users/1",
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    @pytest.mark.parametrize(
        "incorrect_field_in_payload", [
            pytest.param({"avatar": "//reqres.in/img/faces/1-image.jpg"}, id='incorrect avatar'),
            pytest.param({"email": "george.bluthreqres.in"}, id='incorrect email'),
            pytest.param({"first_name": 1}, id='incorrect first_name'),
            pytest.param({"last_name": 1}, id='incorrect last_name'),
            pytest.param({"1last_name": 1}, id='unsupported field 1last_name'),
        ],
    )
    def test_update_with_incorrect_payload(self, app_url: str, incorrect_field_in_payload: dict):
        response: Response = requests.patch(
            f"{app_url}/api/users/1",
            json=incorrect_field_in_payload
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    def test_post(self, app_url: str, db_mydb: 'MyDB'):
        payload_template = {
            "email": "george.bluth@reqres.in",
            "first_name": "11111111morph2e56s",
            "last_name": "Bluth",
            "avatar": "http://reqres.in/img/faces/1-image.jpg"
        }
        response: Response = requests.post(
            f"{app_url}/api/users/",
            json=payload_template,
        )
        assert response.status_code == HTTPStatus.CREATED
        assert db_mydb.get_answer_in_form_of_dictionary(
            'select email, first_name, last_name, avatar from users'
            f' where id = {response.json()["id"]}',
        )[0] == payload_template

    @pytest.mark.parametrize(
        "incorrect_field_in_payload", [
            pytest.param({"avatar": "//reqres.in/img/faces/1-image.jpg"}, id='incorrect avatar'),
            pytest.param({"email": "george.bluthreqres.in"}, id='incorrect email'),
            pytest.param({"first_name": 1}, id='incorrect first_name'),
            pytest.param({"last_name": 1}, id='incorrect last_name'),
            pytest.param({"1last_name": 1}, id='unsupported field 1last_name'),
        ],
    )
    def test_post_with_incorrect_payload(self, app_url: str, incorrect_field_in_payload: dict):
        payload_template = {
            "email": "george.bluth@reqres.in",
            "first_name": "11111111morph2e56s",
            "last_name": "Bluth",
            "avatar": "http://reqres.in/img/faces/1-image.jpg"
        }
        response: Response = requests.post(
            f"{app_url}/api/users/",
            json=payload_template.update(incorrect_field_in_payload)
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    def test_post_without_required_field(self, app_url: str):
        response: Response = requests.post(
            f"{app_url}/api/users/",
            json={
                "first_name": "11111111morph2e56s",
                "last_name": "Bluth",
                "avatar": "http://reqres.in/img/faces/1-image.jpg"
            }
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    def test_post_without_payload(self, app_url: str):
        response: Response = requests.post(
            f"{app_url}/api/users/",
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    def test_post_incorrect_path_in_url(self, app_url: str):
        response: Response = requests.post(
            f"{app_url}/api/users/1",
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
        ErrorParams.model_validate(response.json())

    def test_delete_incorrect_path_in_url(self, app_url: str):
        response: Response = requests.delete(
            f"{app_url}/api/users/",
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
        ErrorParams.model_validate(response.json())

    def test_delete(self, app_url: str, db_mydb: 'MyDB'):
        response: Response = requests.delete(
            f"{app_url}/api/users/1",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"message": "User deleted"}
        assert not len(db_mydb.get_value('select first_name from users where id = 1'))

    def test_delete_non_existent_user(self, app_url: str, db_mydb: 'MyDB'):
        non_existent_user_id: int = db_mydb.get_value(
            'select id from users order by id desc'
        )[0][0] + 1
        response: Response = requests.delete(
            f"{app_url}/api/users/{non_existent_user_id}",
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {"detail": "User not found"}
        assert not len(db_mydb.get_value(
            f'select first_name from users where id = {non_existent_user_id}')
        )

    def test_delete_deleted_user(self, app_url: str, db_mydb: 'MyDB'):
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
