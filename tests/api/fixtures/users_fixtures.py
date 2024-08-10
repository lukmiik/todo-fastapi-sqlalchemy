import pytest

from src.db.models import Users


@pytest.fixture
def user_create_request() -> dict[str, str | bool]:
    return {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "username": "test_username",
        "email": "test@email.com",
        "password": "test_password",
        "is_active": True,
        "role": "admin",
    }


@pytest.fixture
def user_create_response() -> dict[str, str | bool | int]:
    return {
        "id": 1,
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "username": "test_username",
        "email": "test@email.com",
        "is_active": True,
        "role": "admin",
    }


@pytest.fixture
def user_create_request_only_required_data() -> dict[str, str]:
    return {
        "first_name": "test_first_name",
        "username": "test_username",
        "email": "test@email.com",
        "password": "test_password",
    }


@pytest.fixture
def user_create_response_only_required_data() -> dict[str, str | bool | int | None]:
    return {
        "id": 1,
        "first_name": "test_first_name",
        "last_name": "",
        "username": "test_username",
        "email": "test@email.com",
        "is_active": False,
        "role": "user",
    }


@pytest.fixture
def user_for_change_password() -> dict[str, str | bool]:
    return {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "username": "test_username",
        "email": "test@email.com",
        "password": "test_password",
        "is_active": True,
        "role": "ADMIN",
    }


@pytest.fixture
def user_change_password_request() -> dict[str, str]:
    return {
        "username": "test_username",
        "password": "test_password",
        "new_password": "new_test_password",
    }


@pytest.fixture
def user_change_password_wrong_username_request() -> dict[str, str]:
    return {
        "username": "test_wrong_username",
        "password": "test_password",
        "new_password": "new_test_password",
    }


@pytest.fixture
def user_change_password_wrong_password_request() -> dict[str, str]:
    return {
        "username": "test_username",
        "password": "test_wrong_password",
        "new_password": "new_test_password",
    }


@pytest.fixture
async def create_user_in_db(db_session):
    user_data: dict[str, str | bool] = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "username": "test_username",
        "email": "test@email.com",
        "password": "test_password",
        "is_active": True,
        "role": "USER",
    }
    new_user = Users(**user_data)
    db_session.add(new_user)
    db_session.commit()
    yield new_user
    db_session.delete(new_user)
    db_session.commit()
