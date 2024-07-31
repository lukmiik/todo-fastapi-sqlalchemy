from typing import Any, AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def test_client() -> Generator[TestClient, Any, None]:
    yield TestClient(app)


@pytest.fixture
async def async_test_client(
    test_client: TestClient,
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url=test_client.base_url) as client:
        yield client
    # async with AsyncClient(
    #     transport=ASGITransport(app=app), base_url=test_client.base_url
    # ) as client:
    #     yield client
