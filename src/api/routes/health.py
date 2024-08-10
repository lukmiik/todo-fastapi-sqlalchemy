from fastapi import APIRouter

from src.api.schemas.health import HealthCheck

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthCheck)
async def health_check() -> HealthCheck:
    """Endpoint to perform a health check on.

    Returns:
        HealthCheck: JSON response with the health status.
    """
    return HealthCheck(status="ok")
