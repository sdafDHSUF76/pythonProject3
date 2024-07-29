from http import HTTPStatus

import requests
from requests import Response


def test_server_is_ready(app_url: str):
    """Проверяем, готов ли сервер к тестированию."""
    response: Response = requests.get(f"{app_url}/status")
    assert response.status_code == HTTPStatus.OK
