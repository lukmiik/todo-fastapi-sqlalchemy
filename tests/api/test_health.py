import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_health_check(async_test_client: AsyncClient) -> None:
    response = await async_test_client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
