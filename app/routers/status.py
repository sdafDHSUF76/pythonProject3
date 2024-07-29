from http import HTTPStatus

from fastapi import APIRouter, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.engine import engine

router = APIRouter()


@router.get("/status", status_code=HTTPStatus.OK)
def status(response: Response):
    """Ендпоинт для проверки готовности сервера к тестированию.

    При готовности возвращает 200 статус ответа, если не готов сервер 500 статуст ответа.
    """
    try:
        with Session(engine) as session:
            session.execute(text('SELECT 1'))
    except Exception:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
