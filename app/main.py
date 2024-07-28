import json
import os
from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, HTTPException, Response
# from fastapi_pagination import Page, add_pagination, paginate

# from shemas.user import User, Users

# app = FastAPI()
# add_pagination(app)
# users: Users | list = []
import dotenv

dotenv.load_dotenv('C:\\Users\\Y\\pythonProject3\\.env.sample')


import uvicorn
from fastapi import FastAPI

from app.routers import status, users


app = FastAPI()
app.include_router(status.router)
app.include_router(users.router)




#
# @app.get("/status", status_code=HTTPStatus.OK)
# def status(response: Response):
#     """Ендпоинт для проверки готовности сервера к тестированию.
#
#     При готовности возвращает 200 статус ответа, если не готов сервер 500 статуст ответа.
#     """
#     if not bool(users):
#         response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
#
#
# @app.get("/api/users/{user_id}", status_code=HTTPStatus.OK)
# def get_user(user_id: int) -> User:
#     """Получение конкретного юзера.
#
#     Код не мой, но отсавил.
#     """
#     if user_id < 1:
#         raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
#     if user_id > len(users):
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
#     return users[user_id - 1]
#
#
# @app.get("/api/users/", status_code=HTTPStatus.OK)
# def get_users() -> Page[User]:
#     """Получение всех юзеров.
#
#     Используется пагинация.
#     """
#     return paginate(users)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)
