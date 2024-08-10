import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.db.models import Users

pytest_plugins: str = "tests.api.fixtures.users_fixtures"

# make all tests mark with `anyio`
pytestmark = pytest.mark.anyio


async def test_user_create(
    async_test_client: AsyncClient,
    user_create_request,
    user_create_response,
) -> None:
    response = await async_test_client.post("/users/create/", json=user_create_request)
    assert response.status_code == 201
    assert response.json() == user_create_response


async def test_user_create_check_db_record(
    async_test_client: AsyncClient, db_session: Session, user_create_request
) -> None:
    response = await async_test_client.post("/users/create/", json=user_create_request)
    assert response.status_code == 201

    new_user = (
        db_session.query(Users)
        .filter(Users.email == user_create_request["email"])
        .one_or_none()
    )

    assert new_user is not None
    assert new_user.email == user_create_request["email"]
    assert new_user.username == user_create_request["username"]
    assert new_user.first_name == user_create_request["first_name"]
    assert new_user.last_name == user_create_request["last_name"]
    assert new_user.is_active == user_create_request["is_active"]
    assert new_user.role.value == user_create_request["role"]
    assert new_user.password == user_create_request["password"]
    assert new_user.id == 1


async def test_user_create_no_payload(async_test_client: AsyncClient) -> None:
    response = await async_test_client.post("/users/create/")
    assert response.status_code == 422


async def test_user_create_additional_data_in_payload(
    async_test_client: AsyncClient, user_create_request, user_create_response
) -> None:
    payload: dict = user_create_request | {"wrong_random_key": 50}
    response = await async_test_client.post("/users/create/", json=payload)

    assert response.status_code == 201
    assert response.json() == user_create_response


async def test_user_create_only_required_data_in_payload(
    async_test_client: AsyncClient,
    db_session: Session,
    user_create_request_only_required_data,
    user_create_response_only_required_data,
) -> None:
    response = await async_test_client.post(
        "/users/create/", json=user_create_request_only_required_data
    )

    assert response.status_code == 201
    assert response.json() == user_create_response_only_required_data

    new_user = (
        db_session.query(Users)
        .filter(Users.email == user_create_request_only_required_data["email"])
        .one_or_none()
    )

    assert new_user is not None
    assert new_user.email == user_create_response_only_required_data["email"]
    assert new_user.username == user_create_response_only_required_data["username"]
    assert new_user.first_name == user_create_response_only_required_data["first_name"]
    assert new_user.last_name == user_create_response_only_required_data["last_name"]
    assert new_user.is_active == user_create_response_only_required_data["is_active"]
    assert new_user.role.value == user_create_response_only_required_data["role"]
    assert new_user.password == user_create_request_only_required_data["password"]
    assert new_user.id == 1


async def test_user_create_create_same_user_twice(
    async_test_client: AsyncClient, user_create_request, user_create_response
) -> None:
    response = await async_test_client.post("/users/create/", json=user_create_request)

    assert response.status_code == 201
    assert response.json() == user_create_response

    response = await async_test_client.post("/users/create/", json=user_create_request)
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed to create user. Integrity error."}


async def test_user_change_password(
    async_test_client: AsyncClient,
    db_session: Session,
    user_for_change_password,
    user_change_password_request,
) -> None:
    db_session.add(Users(**user_for_change_password))
    db_session.commit()

    response = await async_test_client.post(
        "/users/change_password/", json=user_change_password_request
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Password successfully changed"}


async def test_user_change_password_wrong_username(
    async_test_client: AsyncClient,
    db_session: Session,
    user_for_change_password,
    user_change_password_wrong_username_request,
) -> None:
    db_session.add(Users(**user_for_change_password))
    db_session.commit()

    response = await async_test_client.post(
        "/users/change_password/", json=user_change_password_wrong_username_request
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User with given username not found."}


async def test_user_change_password_wrong_password(
    async_test_client: AsyncClient,
    db_session: Session,
    user_for_change_password,
    user_change_password_wrong_password_request,
) -> None:
    db_session.add(Users(**user_for_change_password))
    db_session.commit()

    response = await async_test_client.post(
        "/users/change_password/", json=user_change_password_wrong_password_request
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Provided current password is incorrect."}
