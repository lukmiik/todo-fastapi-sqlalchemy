from pydantic import BaseModel, EmailStr

from src.db.models import RoleEnum


class UserCreateRequest(BaseModel):
    """Model for validating user create request."""

    first_name: str
    last_name: str | None = None
    username: str
    email: EmailStr
    password: str
    is_active: bool | None = None
    role: RoleEnum | None = RoleEnum.USER


class UserCreateResponse(BaseModel):
    """Model for user create response."""

    id: int
    first_name: str
    last_name: str | None
    username: str
    email: EmailStr
    is_active: bool
    role: RoleEnum
