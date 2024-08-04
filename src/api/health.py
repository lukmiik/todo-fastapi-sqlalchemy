from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthCheck(BaseModel):
    """Model for response health check."""

    status: str = "ok"


@router.get("/", response_model=HealthCheck)
async def health_check() -> HealthCheck:
    """Endpoint to perform a health check on.

    Returns:
        HealthCheck: JSON response with the health status.
    """
    return HealthCheck(status="ok")
