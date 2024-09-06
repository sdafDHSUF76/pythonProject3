from http import HTTPStatus
from typing import TYPE_CHECKING

import requests
from requests import Response
if TYPE_CHECKING:

    from tests.microservice_api import MicroserviceApi


def test_server_is_ready(microservice_api: 'MicroserviceApi'):
    """Проверяем, готов ли сервер к тестированию."""
    response: Response = microservice_api.get_status()
    assert response.status_code == HTTPStatus.OK
