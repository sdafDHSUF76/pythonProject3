import os
from urllib.parse import urljoin
from urllib.request import Request

import dotenv
from requests import Session, Response

from app.shemas.user import UserCreate, UserUpdate


class MicroserviceApi(Session):
    def __init__(self, env: str):
        super().__init__()
        part_of_way: str = os.path.abspath(__file__).split('tests')[0]
        {
            'test': dotenv.load_dotenv(''.join((part_of_way, '.env.docker'))),
            'dev': dotenv.load_dotenv(''.join((part_of_way, '.env.docker'))),
            'preprod': dotenv.load_dotenv(''.join((part_of_way, '.env.docker'))),
        }[env]  # не стал создавать .env.dev, .env.preprod и так тоже хорошо выглядит
        self.base_url = f'{os.getenv("APP_URL")}/api/users/'

    def request(self, method: str, url: str, **another_data_for_request) -> Response:
        full_url = urljoin(self.base_url, url)
        return super().request(method, full_url, **another_data_for_request)

    def get_user(self, user_id: int) -> Response:
        return self.request('get', f'{user_id}')

    def get_users(self, page: int | None = None, per_page: int | None = None) -> Response:
        page_param: str = f'page={page}' if page else ''
        per_page_param: str = f'per_page={per_page}' if per_page else ''
        url_with_params: str = f'?{page_param}&{per_page_param}' if page or per_page else ''
        return self.request('get', f'{url_with_params}')

    def create_user(self, user: UserCreate | None = None) -> Response:
        if user:
            return self.request('post', '/', json=user.dict())
        else:
            return self.request('post', '/', json=user.dict())

    def update_user(self, user_id: int, payload: UserUpdate | None = None) -> Response:
        if payload:
            return self.request('patch', f'/{user_id}', json=payload.dict())
        else:
            return self.request('patch', f'/{user_id}')

    def delete_user(self, user_id: int | None = None) -> Response:
        if user_id:
            return self.request('delete', f'/{user_id}')
        else:
            return self.request('delete', '/')

    def get_status(self) -> Response:
        return self.request('get', '/status')

