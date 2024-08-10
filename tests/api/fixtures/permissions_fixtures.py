import pytest
from sqlalchemy.orm import Session

from src.db.models import Users

ACTIVE_ADMIN_USER_DATA: dict[str, str | bool] = {
    "first_name": "test_first_name",
    "last_name": "test_last_name",
    "username": "test_username",
    "email": "test@email.com",
    "password": "test_password",
    "is_active": True,
    "role": "ADMIN",
}


ACTIVE_USER_USER_DATA: dict[str, str | bool] = {
    "first_name": "test_first_name",
    "last_name": "test_last_name",
    "username": "test_username1",
    "email": "test1@email.com",
    "password": "test_password",
    "is_active": True,
    "role": "USER",
}


@pytest.fixture
async def create_active_admin_user(db_session: Session) -> Users:
    user = Users(**ACTIVE_ADMIN_USER_DATA)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
async def create_active_user_user(db_session: Session) -> Users:
    user = Users(**ACTIVE_USER_USER_DATA)
    db_session.add(user)
    db_session.commit()
    return user
