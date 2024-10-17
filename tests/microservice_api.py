from requests import Response, Session

from app.shemas.user import UserCreate, UserUpdate
from tests.shemas import Configs


class MicroserviceApi(Session):
    def __init__(self, env: Configs):
        super().__init__()
        self.base_url = env.base_url

    def request(self, method: str, url: str, **another_data_for_request) -> Response:
        full_url = ''.join((self.base_url, url))
        return super().request(method, full_url, **another_data_for_request)

    def get_user(self, user_id: int) -> Response:
        return self.request('get', f'/api/users/{user_id}')

    def get_users(self, page: int | None = None, per_page: int | None = None) -> Response:
        page_param: str = f'page={page}' if page is not None else ''
        per_page_param: str = f'per_page={per_page}' if per_page is not None else ''
        url_with_params: str = (
            f'?{page_param}&{per_page_param}' if page is not None or per_page is not None else ''
        )
        return self.request('get', f'/api/users/{url_with_params}')

    def create_user(
        self,
        user: UserCreate | dict | None = None,
        exclude_unset: bool = True,
        path_extension: str = '',
    ) -> Response:
        """url - лишь для одного теста нужно, чтобы проверить, что 404 приходит.

        думал, создавать отедльный метод на это будет копипаста, или не использовать MicroserviceApi
        для api вызовов, тоже считал неправильно... пришлось так сделать.
        """
        if isinstance(user, UserCreate):
            return self.request(
                'post', f'/api/users/{path_extension}', json=user.dict(exclude_unset=exclude_unset),
            )
        elif isinstance(user, dict):
            return self.request('post', f'/api/users/{path_extension}', json=user)
        else:
            return self.request('post', f'/api/users/{path_extension}')

    def update_user(
        self, user_id: int, payload: UserUpdate | dict | None = None, exclude_unset: bool = True,
    ) -> Response:
        if isinstance(payload, UserUpdate):
            return self.request(
                'patch', f'/api/users/{user_id}', json=payload.dict(exclude_unset=exclude_unset),
            )
        elif isinstance(payload, dict):
            return self.request(
                'patch', f'/api/users/{user_id}', json=payload,
            )
        else:
            return self.request('patch', f'/api/users/{user_id}')

    def delete_user(self, user_id: int | None = None) -> Response:
        if user_id:
            return self.request('delete', f'/api/users/{user_id}')
        else:
            return self.request('delete', '/api/users/')

    def get_status(self) -> Response:
        return self.request('get', '/status')
