from sqlalchemy import create_engine, Engine
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_HOST = '127.0.0.1'
DB_PORT = 5436
DB_USER = 'myuser'
DB_PASS = 'mypassword'
DB_NAME = 'mydb'

DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine: Engine = create_engine(DATABASE_URL)

sync_session_maker = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

