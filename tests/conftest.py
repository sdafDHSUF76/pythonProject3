import os
from typing import TYPE_CHECKING

import dotenv
import pytest
from _pytest.python import Function

from tests.tests.test_smoke import test_server_is_ready

if TYPE_CHECKING:
    from _pytest.main import Session


@pytest.fixture(scope='session', autouse=True)
def create_envs():
    """Создаем переменные окружения на компьютере.

    Код не мой, но решил оставить.
    """
    dotenv.load_dotenv(''.join((os.path.abspath(__file__).split('tests')[0], '.env.sample')))


@pytest.fixture(scope='session')
def app_url() -> str:
    """Получение из переменной окружения переменной APP_URL.

    Код не мой, но решил оставить как есть.
    """
    return os.getenv("APP_URL")


def pytest_collection_modifyitems(items: list[Function]):
    """Хук для добавления в коллекцию смоук теста, добавляем в конец после любого запущенного теста.

    Так мы даем возможность запустить смоук тест, в другом хуке, даже если мы запускаем не смоук
    тест. Ну и да, если мы запустили первым смоук тест, то эту логику хука не применяем.
    """
    for item in items:
        if item.originalname == 'test_server_is_ready':
            return
    new_test: Function = pytest.Function.from_parent(
        parent=items[0].parent,
        name=test_server_is_ready.__name__,
        callobj=test_server_is_ready
    )
    items.append(new_test)


def pytest_runtestloop(session: 'Session'):
    """Помогает запустить смоук тест перед любым тестом.

    Если первым тестом мы выбрали запустить смоук тест, то мы не запускаем эту логику запуска
    "Первым запускаем смоук тест", так как он и так запустится. Но если мы запустили любой другой
    тест, то обязательно запустим смоук тест, и удалим его из очереди тестов(чтобы он два раза не
    запускался). Если после прогона смоук тест упал, то останавливаем тестирование
    """
    if session.items[0].originalname != test_server_is_ready.__name__:
        session.ihook.pytest_runtest_protocol(item=session.items[-1], nextitem=None)
        if session.testsfailed:
            session.shouldstop = True
        session.items.remove(session.items[-1])
