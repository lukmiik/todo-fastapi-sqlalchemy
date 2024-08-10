from typing import Annotated

from fastapi import Depends, HTTPException

from src.api.routes.auth import get_current_active_user
from src.db.models import RoleEnum, Users


async def is_admin(
    current_user: Annotated[Users, Depends(get_current_active_user)],
) -> Users:
    """Checks if current user is an admin.

    Args:
        current_user (Annotated[Users, Depends): current user

    Raises:
        HTTPException: forbidden, user is not an admin

    Returns:
        Users: current user
    """
    if current_user.role == RoleEnum.ADMIN:
        return current_user
    raise HTTPException(status_code=403, detail="Forbidden")


async def is_user(
    current_user: Annotated[Users, Depends(get_current_active_user)],
) -> Users:
    """Checks if current user is an user.

    Args:
        current_user (Annotated[Users, Depends): current user

    Raises:
        HTTPException: forbidden, user is not an user

    Returns:
        Users: current user
    """
    if current_user.role == RoleEnum.USER:
        return current_user
    raise HTTPException(status_code=403, detail="Forbidden")


async def is_user_or_is_admin(
    current_user: Annotated[Users, Depends(get_current_active_user)],
) -> Users:
    """Checks if current user is an user or an admin.

    Args:
        current_user (Annotated[Users, Depends): current_user

    Raises:
        HTTPException: forbidden, user is neither user or admin

    Returns:
        Users: current user
    """
    if current_user.role in [RoleEnum.ADMIN, RoleEnum.USER]:
        return current_user
    raise HTTPException(status_code=403, detail="Forbidden")


IsAdminDep = Annotated[Users, Depends(is_admin)]
IsUserDep = Annotated[Users, Depends(is_user)]
IsUserOrAdminDep = Annotated[Users, Depends(is_user_or_is_admin)]
