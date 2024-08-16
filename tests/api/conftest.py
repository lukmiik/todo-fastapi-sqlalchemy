from typing import Any, AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.routes.auth import get_current_active_user
from src.db.base import Base
from src.db.dependency import get_db
from src.db.models import Users
from src.main import app

SQLITE_DATABASE_URL = "sqlite:///./test_db.db"

engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def test_client() -> Generator[TestClient, Any, None]:
    yield TestClient(app)


# scope = "function", which means it will be set up and torn down
# for each individual test function.
@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
async def async_test_client(
    test_client: TestClient, db_session
) -> AsyncGenerator[AsyncClient, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url=test_client.base_url) as client:
        yield client


USER_DATA: dict[str, str | bool] = {
    "first_name": "test_auth_first_name",
    "last_name": "test_auth_last_name",
    "username": "test_auth_username",
    "email": "testauth_@email.com",
    "password": "test_auth_password",
    "is_active": True,
    "role": "USER",
}


ADMIN_USER_DATA: dict[str, str | bool] = {
    "first_name": "test_auth_admin_first_name",
    "last_name": "test_auth_admin_last_name",
    "username": "test_auth_admin_username",
    "email": "test_auth_admin@email.com",
    "password": "test_auth_admin_password",
    "is_active": True,
    "role": "ADMIN",
}


@pytest.fixture(scope="function")
async def auth_user_async_test_client(
    async_test_client: AsyncClient, db_session: Session
) -> AsyncGenerator[tuple[AsyncClient, Users], None]:
    user = Users(**USER_DATA)
    db_session.add(user)
    db_session.commit()

    app.dependency_overrides[get_current_active_user] = lambda: user

    yield async_test_client, user

    app.dependency_overrides = {}


@pytest.fixture(scope="function")
async def auth_admin_async_test_client(
    async_test_client: AsyncClient, db_session: Session
) -> AsyncGenerator[tuple[AsyncClient, Users], None]:
    admin_user = Users(**ADMIN_USER_DATA)
    db_session.add(admin_user)
    db_session.commit()

    app.dependency_overrides[get_current_active_user] = lambda: admin_user

    yield async_test_client, admin_user

    app.dependency_overrides = {}
