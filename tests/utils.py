from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests.fixtures.database import MyDB


def calculate_pages(total: int, size: int) -> int:
    """рассчитать pages.

    Получаем Pages по total, size параметрам.
    """
    if total > size:
        return total // size + (1 if total % size else 0)
    else:
        return 1


def fill_users_table(connect_postgres: 'MyDB') -> None:
    """Заполняем базу данных нужными записями."""
    connect_postgres.execute(
        'TRUNCATE users;\n'
        'ALTER SEQUENCE users_id_seq RESTART WITH 1;\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'george.bluth@reqres.in', 'George', 'Bluth', 'https://reqres.in/img/faces/1-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'anet.weaver@reqres.in', 'Janet', 'Weaver', 'https://reqres.in/img/faces/2-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'emma.wong@reqres.in', 'Emma', 'Wong', 'https://reqres.in/img/faces/3-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'eve.holt@reqres.in', 'Eve', 'Holt', 'https://reqres.in/img/faces/4-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'charles.morris@reqres.in', 'Charles', 'Morris', 'https://reqres.in/img/faces/5-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'tracey.ramos@reqres.in', 'Tracey', 'Ramos', 'https://reqres.in/img/faces/6-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'michael.lawson@reqres.in', 'Michael', 'Lawson', 'https://reqres.in/img/faces/7-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'lindsay.ferguson@reqres.in', 'Lindsay', 'Ferguson',"
        " 'https://reqres.in/img/faces/8-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'tobias.funke@reqres.in', 'Tobias', 'Funke', 'https://reqres.in/img/faces/9-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'byron.fields@reqres.in', 'Byron', 'Fields', 'https://reqres.in/img/faces/10-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'george.edwards@reqres.in', 'George', 'Edwards',"
        " 'https://reqres.in/img/faces/11-image.jpg'"
        ');\n'
        'insert into users (email, first_name , last_name , avatar )'
        ' values ('
        "'rachel.howell@reqres.in', 'Rachel', 'Howell', 'https://reqres.in/img/faces/12-image.jpg'"
        ');\n'
    )
