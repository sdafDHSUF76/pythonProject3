import psycopg2
import pytest
import structlog as structlog
# from psycopg2 import cursor
logger = structlog.get_logger('sql')




@pytest.fixture(scope='session')
def connect() -> psycopg2:
    postgresql = psycopg2.connect(
        dbname='mydb',
        user='myuser',
        password='mypassword',
        host='127.0.0.1',
        port='5436',
    )
    postgresql.autocommit = True  # автокомментирование после execute делает
    yield postgresql
    postgresql.close()




class MyDB:
    def __init__(self, connect: psycopg2):
        self.conn = connect

    def get_db_name(self) -> str:
        """Get database name."""
        return self.conn.dsn.split(' ')[2].split('=')[1]

    def _execute_query(self, query: str):
        logger.info('SQL query request', db=self.get_db_name(), query=query)
        with self.conn, self.conn.cursor() as cursor:
            return cursor

    def get_value(self, query: str) -> list[tuple[str | int, ...], ...]:
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
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            self.conn.commit()
            logger.info('SQL result', db=self.get_db_name(), query=query)
            # self.conn.close()
            # return result
        # self._execute_query(query)



    def close(self) -> None:
        self.conn.close()


@pytest.fixture(scope='session')
def db_mydb(connect: psycopg2) -> MyDB:
    mydb: MyDB = MyDB(connect)
    yield mydb
    mydb.close()
