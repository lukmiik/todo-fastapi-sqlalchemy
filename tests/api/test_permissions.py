import pytest
from fastapi import HTTPException

from src.api.permissions import is_admin, is_user, is_user_or_is_admin
from src.db.models import Users

pytest_plugins = "tests.api.fixtures.permissions_fixtures"

pytestmark = pytest.mark.anyio


async def test_is_admin(create_active_admin_user: Users) -> None:
    # overriding dependency with create_active_admin_user
    user = await is_admin(current_user=create_active_admin_user)

    assert user == create_active_admin_user


async def test_is_admin_not_admin_user_role(create_active_user_user: Users) -> None:
    # overriding dependency with create_active_user_user
    with pytest.raises(HTTPException) as err:
        await is_admin(current_user=create_active_user_user)

    assert err.value.status_code == 403
    assert err.value.detail == "Forbidden"


async def test_is_user(create_active_user_user: Users) -> None:
    # overriding dependency with create_active_user_user
    user = await is_user(current_user=create_active_user_user)

    assert user == create_active_user_user


async def test_is_user_not_user_user_role(create_active_admin_user: Users) -> None:
    # overriding dependency with create_active_admin_user
    with pytest.raises(HTTPException) as err:
        x = await is_user(current_user=create_active_admin_user)
        print("x: ", x)

    assert err.value.status_code == 403
    assert err.value.detail == "Forbidden"


async def test_is_user_or_is_admin(
    create_active_admin_user: Users, create_active_user_user: Users
) -> None:
    # overriding dependency with create_active_admin_user
    user = await is_user_or_is_admin(current_user=create_active_admin_user)

    assert user == create_active_admin_user

    user = await is_user_or_is_admin(current_user=create_active_user_user)

    assert user == create_active_user_user
