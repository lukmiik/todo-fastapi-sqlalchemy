from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Model for response health check."""

    status: str = "ok"
