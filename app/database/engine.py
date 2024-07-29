import os

import dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase

dotenv.load_dotenv(''.join((os.path.abspath(__file__).split('app')[0], '.env.sample')))

DB_HOST = os.getenv('HOST_DB')
DB_PORT = os.getenv('PORT_DB')
DB_USER = os.getenv('USER_NAME')
DB_PASS = os.getenv('PASSWORD_FOR_DB')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine: Engine = create_engine(
    DATABASE_URL,
    # pool_size=os.getenv("DATABASE_POOL_SIZE", 10)
)


class Base(DeclarativeBase):
    pass
