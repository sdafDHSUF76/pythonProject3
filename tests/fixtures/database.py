import os

import dotenv
import psycopg2
import pytest
import structlog as structlog

dotenv.load_dotenv(''.join((os.path.abspath(__file__).split('tests')[0], '.env.sample')))
logger = structlog.get_logger('sql')
configs_for_db = dict(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('USER_NAME'),
    password=os.getenv('PASSWORD_FOR_DB'),
    host=os.getenv('HOST_DB'),
    port=os.getenv('PORT_DB')
)


@pytest.fixture(scope='session')
def connect() -> psycopg2:
    """Получаем соединение к базе данных."""
    postgresql = psycopg2.connect(**configs_for_db)
    postgresql.autocommit = True  # автокомментирование после execute делает
    yield postgresql
    postgresql.close()


class MyDB:
    """Содержит методы, для обращения в базу данных."""
    def __init__(self, connect: psycopg2):
        self.conn = connect

    def get_db_name(self) -> str:
        """Get database name."""
        return self.conn.dsn.split(' ')[2].split('=')[1]

    def get_value(self, query: str) -> list[tuple[str | int, ...], ...]:
        """Получаем значения из базы данных"""
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            self.conn.commit()
            result = cursor.fetchall()
            logger.info('SQL result', db=self.get_db_name(), query=query, result=result)
            return result

    def get_answer_in_form_of_dictionary(self, query: str) -> list[dict]:
        """get list of dicts with column names and values from database of query."""
        result = []
        data = {}
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            for unit_of_data_received in cursor:
                for id, col in enumerate(cursor.description):
                    data.update({col[0]: unit_of_data_received[id]})
                result.append(data.copy())
                data.clear()
            logger.info('SQL result', db=self.get_db_name(), query=query, result=result)
            return result

    def execute(self, query: str) -> None:
        """Выполнить определенный запрос, например Insert, Update,...все что кроме select."""
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            self.conn.commit()
            logger.info('SQL result', db=self.get_db_name(), query=query)

    def close(self) -> None:
        """Закрыть подключение к базе данных."""
        self.conn.close()


@pytest.fixture(scope='session')
def db_mydb(connect: psycopg2) -> MyDB:
    """Получаем доступ к базе данных, чтобы делать в ней запросы."""
    mydb: MyDB = MyDB(connect)
    yield mydb
    mydb.close()
