from http import HTTPStatus
from typing import TYPE_CHECKING

import faker as faker
import pytest
from requests import Response

from app.shemas.error_list import ErrorParams
from app.shemas.user import User, UserCreate, Users, UserUpdate
from tests.fixtures.database import connect, db_mydb  # noqa F401

if TYPE_CHECKING:
    from tests.fixtures.database import MyDB
    from tests.microservice_api import MicroserviceApi


@pytest.mark.usefixtures('prepare_table_users')
class TestsApi:
    def tests_users_no_duplicates(self, microservice_api: 'MicroserviceApi'):
        response: Response = microservice_api.get_users()
        users_ids = [user["id"] for user in response.json()['data']]
        assert len(users_ids) == len(set(users_ids))

    @pytest.mark.parametrize("user_id", [1, 6, 12])
    def test_user_id(self, microservice_api: 'MicroserviceApi', user_id: int):
        response: Response = microservice_api.get_user(user_id)
        assert response.status_code == HTTPStatus.OK
        User.model_validate(response.json())

    @pytest.mark.parametrize("user_id", [13])
    def test_user_nonexistent_values(self, microservice_api: 'MicroserviceApi', user_id: int):
        response: Response = microservice_api.get_user(user_id)
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_user_invalid_values(self, microservice_api: 'MicroserviceApi', user_id: int):
        response: Response = microservice_api.get_user(user_id)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_users(self, microservice_api: 'MicroserviceApi'):
        response: Response = microservice_api.get_users()
        assert response.status_code == HTTPStatus.OK
        Users.model_validate(response.json())

    def test_update_one_field_payload(self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB'):
        response: Response = microservice_api.update_user(1, UserUpdate(first_name='1234'))
        assert response.status_code == HTTPStatus.OK
        User.model_validate(response.json())
        assert db_mydb.get_value('select first_name from users where id = 1')[0][0] == '1234'

    @pytest.mark.parametrize(
        'field_name, value',
        [
            ("email", "george.bluth@reqres.in"),
            ("first_name", "11111111morph2e56s"),
            ("last_name", "Bluth"),
            ("avatar", "http://reqres.in/img/faces/1-image.jpg"),
        ]
    )
    def test_update_one_field_payload(
        self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB', field_name: str, value: str,
    ):
        response: Response = microservice_api.update_user(1, UserUpdate(**{field_name: value}))
        assert response.status_code == HTTPStatus.OK
        User.model_validate(response.json())
        assert db_mydb.get_value(f'select {field_name} from users where id = 1')[0][0] == value

    @pytest.mark.parametrize(
        'field_name, value',
        [
            ("email", faker.Faker().free_email()),
            ("first_name", faker.Faker().name().split(' ')[0]),
            ("last_name", faker.Faker().name().split(' ')[1]),
            ("avatar", faker.Faker().image_url()),
        ]
    )
    def test_update_one_field_payload_with_random_valid_data(
        self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB', field_name: str, value: str,
    ):
        user_id: int = faker.Faker().random_choices(
            elements=db_mydb.get_value('select id from users order by id desc')[0],
            length=1,
        )[0]
        response: Response = microservice_api.update_user(
            user_id, UserUpdate(**{field_name: value}),
        )
        assert response.status_code == HTTPStatus.OK
        User.model_validate(response.json())
        assert db_mydb.get_value(
            f'select {field_name} from users where id = {user_id}'
        )[0][0] == value

    def test_update_all_fields(self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB'):
        payload_template = {
            "email": "george.bluth@reqres.in",
            "first_name": "11111111morph2e56s",
            "last_name": "Bluth",
            "avatar": "http://reqres.in/img/faces/1-image.jpg"
        }
        response: Response = microservice_api.update_user(1, UserUpdate(**payload_template))
        assert response.status_code == HTTPStatus.OK
        User.model_validate(response.json())
        assert db_mydb.get_answer_in_form_of_dictionary(
            'select email, first_name, last_name, avatar from users where id = 1'
        )[0] == payload_template

    def test_update_all_fields_with_random_valid_data(
        self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB',
    ):
        payload_template = {
            "email": faker.Faker().free_email(),
            "first_name": faker.Faker().name().split(' ')[0],
            "last_name": faker.Faker().name().split(' ')[1],
            "avatar": faker.Faker().image_url(),
        }
        user_id: int = faker.Faker().random_choices(
            elements=db_mydb.get_value('select id from users order by id desc')[0],
            length=1,
        )[0]
        response: Response = microservice_api.update_user(user_id, UserUpdate(**payload_template))
        assert response.status_code == HTTPStatus.OK
        User.model_validate(response.json())
        assert db_mydb.get_answer_in_form_of_dictionary(
            f'select email, first_name, last_name, avatar from users where id = {user_id}'
        )[0] == payload_template

    def test_update_non_existent_user(self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB'):
        non_existent_user_id: int = db_mydb.get_value(
            'select id from users order by id desc'
        )[0][0] + 1
        response: Response = microservice_api.update_user(
            non_existent_user_id, UserUpdate(**{'first_name': '1234'}),
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'detail': 'User not found'}

    def test_update_without_payload(self, microservice_api: 'MicroserviceApi'):
        response: Response = microservice_api.update_user(1)
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
    def test_update_with_incorrect_payload(
        self, microservice_api: 'MicroserviceApi', incorrect_field_in_payload: dict,
    ):
        response: Response = microservice_api.update_user(
            1, incorrect_field_in_payload,
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    def test_post(self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB'):
        payload_template = {
            "email": "george.bluth@reqres.in",
            "first_name": "11111111morph2e56s",
            "last_name": "Bluth",
            "avatar": "http://reqres.in/img/faces/1-image.jpg"
        }
        response: Response = microservice_api.create_user(UserCreate(**payload_template))
        assert response.status_code == HTTPStatus.CREATED
        assert db_mydb.get_answer_in_form_of_dictionary(
            'select email, first_name, last_name, avatar from users'
            f' where id = {response.json()["id"]}',
        )[0] == payload_template

    def test_post_with_random_valid_data(
        self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB',
    ):
        payload_template = {
            "email": faker.Faker().free_email(),
            "first_name": faker.Faker().name().split(' ')[0],
            "last_name": faker.Faker().name().split(' ')[1],
            "avatar": faker.Faker().image_url()
        }
        response: Response = microservice_api.create_user(UserCreate(**payload_template))
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
    def test_post_with_incorrect_payload(
        self, microservice_api: 'MicroserviceApi', incorrect_field_in_payload: dict,
    ):
        payload_template = {
            "email": "george.bluth@reqres.in",
            "first_name": "11111111morph2e56s",
            "last_name": "Bluth",
            "avatar": "http://reqres.in/img/faces/1-image.jpg"
        }
        new_payload: dict = payload_template.update(incorrect_field_in_payload)
        response: Response = microservice_api.create_user(new_payload)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    def test_post_without_required_field(self, microservice_api: 'MicroserviceApi'):
        response: Response = microservice_api.create_user({
            "first_name": "11111111morph2e56s",
            "last_name": "Bluth",
            "avatar": "http://reqres.in/img/faces/1-image.jpg"
        })
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    def test_post_without_payload(self, microservice_api: 'MicroserviceApi'):
        response: Response = microservice_api.create_user()
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ErrorParams.model_validate(response.json())

    def test_post_incorrect_path_in_url(self, microservice_api: 'MicroserviceApi'):
        response: Response = microservice_api.create_user(path_extension='1')
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
        ErrorParams.model_validate(response.json())

    def test_delete_incorrect_path_in_url(self, microservice_api: 'MicroserviceApi'):
        response: Response = microservice_api.delete_user()
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
        ErrorParams.model_validate(response.json())

    def test_delete(self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB'):
        response: Response = microservice_api.delete_user(1)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"message": "User deleted"}
        assert not len(db_mydb.get_value('select first_name from users where id = 1'))

    def test_delete_with_random_valid_data(
        self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB',
    ):
        user_id: int = faker.Faker().random_choices(
            elements=db_mydb.get_value('select id from users order by id desc')[0],
            length=1,
        )[0]
        response: Response = microservice_api.delete_user(user_id)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"message": "User deleted"}
        assert not len(db_mydb.get_value(f'select first_name from users where id = {user_id}'))

    def test_delete_non_existent_user(self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB'):
        non_existent_user_id: int = db_mydb.get_value(
            'select id from users order by id desc'
        )[0][0] + 1
        response: Response = microservice_api.delete_user(non_existent_user_id)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {"detail": "User not found"}
        assert not len(db_mydb.get_value(
            f'select first_name from users where id = {non_existent_user_id}')
        )

    def test_delete_deleted_user(self, microservice_api: 'MicroserviceApi', db_mydb: 'MyDB'):
        user_id: int = faker.Faker().random_choices(
            elements=db_mydb.get_value('select id from users order by id desc')[0],
            length=1,
        )[0]
        microservice_api.delete_user(user_id)
        response: Response = microservice_api.delete_user(user_id)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {
            "detail": "User not found"
        }
        assert not len(db_mydb.get_value(f'select first_name from users where id = {user_id}'))
