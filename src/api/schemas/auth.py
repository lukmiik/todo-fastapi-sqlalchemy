from pydantic import BaseModel

from src.db.models import RoleEnum


class UserAuth(BaseModel):
    """User model for auth."""

    username: str
    email: str
    first_name: str
    last_name: str | None
    role: RoleEnum
    is_active: bool


class AuthUserIn(BaseModel):
    """User data for authentication."""

    username: str
    password: str


class TokenDataIn(BaseModel):
    """Data used for generating token."""

    sub: str


class Token(BaseModel):
    """JWT Token model."""

    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    """Data from JWT Token."""

    username: str | None = None


class RefreshTokenRequest(BaseModel):
    """Model for refresh token request."""

    refresh_token: str
