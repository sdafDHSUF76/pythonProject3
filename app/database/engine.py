from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase

DB_HOST = '127.0.0.1'
DB_PORT = 5436
DB_USER = 'myuser'
DB_PASS = 'mypassword'
DB_NAME = 'mydb'

DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine: Engine = create_engine(
    DATABASE_URL,
    # pool_size=os.getenv("DATABASE_POOL_SIZE", 10)
)


class Base(DeclarativeBase):
    pass
