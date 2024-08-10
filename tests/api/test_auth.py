from datetime import datetime, timedelta, timezone
from unittest import mock

import jwt
import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.api.routes.auth import (
    AuthUserIn,
    TokenDataIn,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from src.db.models import Users
from src.settings import Settings
from tests.api.utils.tokens import create_access_token as create_access_token_for_tests
from tests.api.utils.tokens import (
    create_refresh_token as create_refresh_token_for_tests,
)

pytest_plugins: list[str] = [
    "tests.api.fixtures.users_fixtures",
]

# make all test mark with `anyio`
pytestmark = pytest.mark.anyio

settings = Settings.get_settings()

TEST_DATETIME_NOW: datetime


async def test_authenticate_user(db_session: Session, create_user_in_db) -> None:
    username: str = create_user_in_db.username
    password: str = create_user_in_db.password
    user_data = AuthUserIn(username=username, password=password)

    auth_user = authenticate_user(db_session, user_data)

    assert isinstance(auth_user, Users)
    assert auth_user == create_user_in_db


async def test_authenticate_user_invalid_username(
    db_session: Session, create_user_in_db
) -> None:
    username: str = create_user_in_db.username
    password: str = create_user_in_db.password
    username += "invalid_username"
    user_data = AuthUserIn(username=username, password=password)

    with pytest.raises(HTTPException) as err:
        authenticate_user(db_session, user_data)

    assert err.value.detail == "Incorrect username or password"
    assert err.value.status_code == 401


async def test_authenticate_user_invalid_password(
    db_session: Session, create_user_in_db
) -> None:
    username: str = create_user_in_db.username
    password: str = create_user_in_db.password
    password += "invalid_password"
    user_data = AuthUserIn(username=username, password=password)

    with pytest.raises(HTTPException) as err:
        authenticate_user(db_session, user_data)

    assert err.value.detail == "Incorrect username or password"
    assert err.value.status_code == 401


@mock.patch("src.api.routes.auth.datetime")
async def test_create_access_token(mock_datetime_now) -> None:
    test_datetime_now = datetime(year=9999, month=10, day=5)
    test_datetime_now = test_datetime_now.replace(tzinfo=timezone.utc)
    mock_datetime_now.now.return_value = test_datetime_now
    username_for_access_token = "test_username_access_token"
    expected_expiration_datetime = test_datetime_now + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    expected_expiration_in_seconds = int(expected_expiration_datetime.timestamp())
    user_data = TokenDataIn(sub=username_for_access_token)
    access_token = create_access_token(data=user_data)

    assert isinstance(access_token, str)

    decoded_access_token = jwt.decode(
        access_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert "sub" in decoded_access_token
    assert "exp" in decoded_access_token

    assert decoded_access_token["sub"] == username_for_access_token
    assert decoded_access_token["exp"] == expected_expiration_in_seconds


@mock.patch("src.api.routes.auth.datetime")
async def test_create_refresh_token(mock_datetime_now) -> None:
    test_datetime_now = datetime(year=9999, month=10, day=5)
    test_datetime_now = test_datetime_now.replace(tzinfo=timezone.utc)
    mock_datetime_now.now.return_value = test_datetime_now
    username_for_refresh_token = "test_username_refresh_token"
    expected_expiration_datetime = test_datetime_now + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    expected_expiration_in_seconds = int(expected_expiration_datetime.timestamp())
    user_data = TokenDataIn(sub=username_for_refresh_token)
    refresh_token = create_refresh_token(data=user_data)

    assert isinstance(refresh_token, str)

    decoded_refresh_token = jwt.decode(
        refresh_token,
        settings.REFRESH_SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert "sub" in decoded_refresh_token
    assert "exp" in decoded_refresh_token

    assert decoded_refresh_token["sub"] == username_for_refresh_token
    assert decoded_refresh_token["exp"] == expected_expiration_in_seconds


async def test_get_current_user(db_session: Session, create_user_in_db: Users) -> None:
    username = create_user_in_db.username
    expire = datetime(year=9999, month=1, day=1)
    data_to_encode: dict = {"sub": username, "exp": expire}

    access_token = jwt.encode(
        data_to_encode,
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )

    user = await get_current_user(db_session, access_token)

    assert user == create_user_in_db


async def test_get_current_user_no_sub_in_token(db_session: Session) -> None:
    expire = datetime(year=9999, month=1, day=1)
    data_to_encode: dict = {"exp": expire}

    access_token = jwt.encode(
        data_to_encode,
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )
    with pytest.raises(HTTPException) as err:
        await get_current_user(db_session, access_token)

    assert err.value.detail == "Could not validate credentials"
    assert err.value.status_code == 401


async def test_get_current_user_invalid_username(
    db_session: Session, create_user_in_db: Users
) -> None:
    username = create_user_in_db.username + "invalid"
    expire = datetime(year=9999, month=1, day=1)
    data_to_encode: dict = {"sub": username, "exp": expire}

    access_token = jwt.encode(
        data_to_encode,
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )

    with pytest.raises(HTTPException) as err:
        await get_current_user(db_session, access_token)

    assert err.value.detail == "Could not validate credentials"
    assert err.value.status_code == 401


async def test_get_current_user_invalid_access_token(
    db_session: Session, create_user_in_db: Users
) -> None:
    username = create_user_in_db.username
    expire = datetime(year=9999, month=1, day=1)
    data_to_encode: dict = {"sub": username, "exp": expire}

    access_token = jwt.encode(
        data_to_encode,
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )
    invalid_access_token = access_token + "invalid"

    with pytest.raises(HTTPException) as err:
        await get_current_user(db_session, invalid_access_token)

    assert err.value.detail == "Invalid access token"
    assert err.value.status_code == 401


@mock.patch("src.api.routes.auth.datetime")
@mock.patch("tests.api.utils.tokens.datetime")
async def test_login(
    mock_datetime_now,
    mock_datetime_now_utils,
    async_test_client: AsyncClient,
    create_user_in_db: Users,
) -> None:
    username = create_user_in_db.username
    password = create_user_in_db.password
    form_data = {"username": username, "password": password}

    test_datetime_now = datetime(year=9999, month=10, day=5)
    test_datetime_now = test_datetime_now.replace(tzinfo=timezone.utc)
    mock_datetime_now.now.return_value = test_datetime_now
    mock_datetime_now_utils.now.return_value = test_datetime_now

    expected_access_token = create_access_token_for_tests(username)
    expected_refresh_token = create_refresh_token_for_tests(username)

    response = await async_test_client.post("/auth/token/", data=form_data)

    content = response.json()

    assert content.get("access_token") == expected_access_token
    assert content.get("refresh_token") == expected_refresh_token
    assert content.get("token_type") == "bearer"


async def test_login_invalid_user_data(
    async_test_client: AsyncClient, create_user_in_db: Users
) -> None:
    username = create_user_in_db.username
    password = create_user_in_db.password
    invalid_username = create_user_in_db.username + "invalid"
    invalid_password = create_user_in_db.password + "invalid"

    form_data = {"username": invalid_username, "password": password}

    response = await async_test_client.post("/auth/token/", data=form_data)

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

    form_data = {"username": username, "password": invalid_password}

    response = await async_test_client.post("/auth/token/", data=form_data)

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


@mock.patch("src.api.routes.auth.datetime")
@mock.patch("tests.api.utils.tokens.datetime")
async def test_refresh(
    mock_datetime_now,
    mock_datetime_now_utils,
    async_test_client: AsyncClient,
    create_user_in_db: Users,
) -> None:
    username = create_user_in_db.username

    test_datetime_now = datetime(year=9999, month=10, day=5)
    test_datetime_now = test_datetime_now.replace(tzinfo=timezone.utc)
    mock_datetime_now.now.return_value = test_datetime_now
    mock_datetime_now_utils.now.return_value = test_datetime_now

    refresh_token = create_refresh_token_for_tests(
        username, test_datetime_now - timedelta(weeks=1)
    )

    expected_access_token = create_access_token_for_tests(username)
    expected_refresh_token = create_refresh_token_for_tests(username)

    response = await async_test_client.post(
        "/auth/token/refresh/", json={"refresh_token": refresh_token}
    )

    content = response.json()

    assert response.status_code == 200
    assert content["access_token"] == expected_access_token
    assert content["refresh_token"] == expected_refresh_token
    assert content["token_type"] == "bearer"


async def test_refresh_invalid_refresh_token(
    async_test_client: AsyncClient, create_user_in_db: Users
) -> None:
    username = create_user_in_db.username

    refresh_token = (
        create_refresh_token_for_tests(
            username, datetime.now(timezone.utc) + timedelta(days=1)
        )
        + "invalid"
    )

    response = await async_test_client.post(
        "/auth/token/refresh/", json={"refresh_token": refresh_token}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


async def test_refresh_no_sub_in_token(async_test_client: AsyncClient) -> None:
    refresh_token = (
        jwt.encode(
            {"exp": datetime.now(timezone.utc) + timedelta(days=1)},
            key=settings.REFRESH_SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        + "invalid"
    )

    response = await async_test_client.post(
        "/auth/token/refresh/", json={"refresh_token": refresh_token}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
