import os
import re
from typing import Iterable

import dotenv
import pytest
import structlog as structlog
from sqlalchemy import Connection, Row, create_engine, text
from sqlalchemy.orm import Session

dotenv.load_dotenv(''.join((os.path.abspath(__file__).split('tests')[0], '.env.sample')))
logger = structlog.get_logger('sql')
configs_for_db = dict(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('USER_NAME'),
    password=os.getenv('PASSWORD_FOR_DB'),
    host=os.getenv('HOST_DB'),
    port=os.getenv('PORT_DB')
)

DB_HOST = os.getenv('HOST_DB')
DB_PORT = os.getenv('PORT_DB')
DB_USER = os.getenv('USER_NAME')
DB_PASS = os.getenv('PASSWORD_FOR_DB')
DB_NAME = os.getenv('DB_NAME')
DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


@pytest.fixture(scope='session')
def connect() -> Connection:
    """Получаем соединение к базе данных."""
    engine: Connection = create_engine(
        DATABASE_URL,
        # pool_size=os.getenv("DATABASE_POOL_SIZE", 10)
    ).connect()
    yield engine
    engine.close()


class MyDB:
    """Содержит методы, для обращения в базу данных."""
    def __init__(self, connect: Connection):
        self.conn = connect

    def get_db_name(self) -> str:
        """Get database name."""
        return self.conn.engine.url.database

    def get_value(self, query: str) -> list[Row]:
        """Получаем значения из базы данных"""

        with Session(self.conn) as session:
            result: Iterable[Row] = session.execute(text(query)).fetchall()
            logger.info('\nSQL result', database=self.get_db_name(), query=query, sql_result=result)
            return list(result)

    def get_answer_in_form_of_dictionary(self, query: str) -> list[dict]:
        """get list of dicts with column names and values from database of query."""
        result = []
        data = {}

        with Session(self.conn) as session:
            result_query: Iterable[Row] = session.execute(text(query)).fetchall()
            table_name: str = query.lower().split('from')[1].strip().split(' ')[0]
            if re.search(r'\*', query):
                columns_names: list[str] = [
                    unit[0] for unit in session.execute(text(
                        "SELECT column_name FROM information_schema.columns"
                        f" WHERE table_name = '{table_name}';"
                    )).fetchall()
                ]
            else:
                columns_names: list[str] = (
                    query.lower().split('from')[0].split('select')[1].strip().replace(' ', '')
                    .split(',')
                )
            for unit_of_data_received in result_query:
                data.update({x: y for x, y in zip(columns_names, unit_of_data_received)})
                result.append(data.copy())
                data.clear()
            logger.info('\nSQL result', database=self.get_db_name(), query=query, sql_result=result)

            return result

    def execute(self, query: str) -> None:
        """Выполнить определенный запрос, например Insert, Update,...все что кроме select."""
        with Session(self.conn) as session:
            session.execute(text(query))
            self.conn.commit()
            logger.info('\nSQL result', database=self.get_db_name(), query=query)

    def close(self) -> None:
        """Закрыть подключение к базе данных."""
        self.conn.close()


@pytest.fixture(scope='session')
def db_mydb(connect: Connection) -> MyDB:
    """Получаем доступ к базе данных, чтобы делать в ней запросы."""
    mydb: MyDB = MyDB(connect)
    yield mydb
    mydb.close()
