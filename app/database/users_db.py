from datetime import datetime
from typing import Iterable, Type

from fastapi import HTTPException
from sqlalchemy import select, update, insert, delete
from sqlalchemy.orm import Session, InstanceState

# from sqlmodel import Session, select
from app.database.engine import engine, Base
from app.models.user import User
from app.shemas.user import User as Userr, UserUpdate, UserCreate


def get_user(user_id: int) -> User | None:
    with Session(engine) as session:
        return session.get(User, user_id)


def _convert_model_to_json(models: Iterable[Base] | Type[Base]) -> Userr | list[Userr]:
    body_result = {}
    if isinstance(models, list):
        result = []
        for unit in models:
            attrs: InstanceState = unit.__dict__.get('_sa_instance_state')
            for unit in attrs.attrs:
                body_result.update({unit.key: unit.loaded_value})
            result.append(Userr(**body_result))
        return result
    else:
        attrs: InstanceState = models.__dict__.get('_sa_instance_state')
        for unit in attrs.attrs:
            body_result.update({unit.key: unit.loaded_value})

        return Userr(**body_result)

def get_users() -> list[Userr]:
    with Session(engine) as session:
        statement = select(User).order_by(User.id.asc())
        result = session.execute(statement)
        result = result.scalars().all()
        # for unit in result:
        #     attrs: InstanceState = unit.__dict__.get('_sa_instance_state')
        #     body_result = {}
        #     for unit in attrs.attrs:
        #         body_result.update({unit.key: unit.loaded_value})
        return _convert_model_to_json(result)


def create_user(user: UserCreate) -> dict:
    with Session(engine) as session:
        session.execute(insert(User).values(**user.dict()))
        session.commit()
        # session.refresh(user)
        result = session.execute(select(User).filter_by(**user.dict()).order_by(User.id.asc()).limit(1)).scalars().all()
        return {
            "name": user.dict().get('first_name'),
            "job": "leader",
            "id": str(result[0].id),
            "createdAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        }


def update_user(user_id: int, user: UserUpdate) -> Userr:
    with Session(engine) as session:
        db_user: Type[User] | None = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        user_data: dict = user.model_dump(exclude_unset=True)
        if user_data:

            session.execute(update(User).values(**user_data).filter_by(id=user_id))
            # db_user.sqlmodel_update(user_data)
            # session.add(db_user)
            session.commit()
        session.refresh(db_user)
        return _convert_model_to_json(db_user)


def delete_user(user_id: int):
    with Session(engine) as session:
        db_user = session.get(User, user_id)
        # db_user = session.execute(select(User).filter_by(**{User.id.name: user_id}))
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        session.execute(delete(User).filter_by(**{User.id.name: user_id}))
        session.commit()
