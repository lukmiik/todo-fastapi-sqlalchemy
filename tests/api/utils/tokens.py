from datetime import datetime, timedelta, timezone

import jwt

from src.settings import Settings


def create_access_token(username: str, expire: datetime | None = None) -> str:
    """Creates access token.

    Args:
        data (TokenDataIn): user data for creating token

    Returns:
        str: encoded jwt access token
    """
    if expire is None:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=Settings.get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode,
        Settings.get_settings().SECRET_KEY,
        algorithm=Settings.get_settings().ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(username: str, expire: datetime | None = None) -> str:
    """Creates refresh token.

    Args:
        data (TokenDataIn): user data for creating token

    Returns:
        str: encoded refresh token
    """
    if expire is None:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=Settings.get_settings().REFRESH_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode,
        Settings.get_settings().REFRESH_SECRET_KEY,
        Settings.get_settings().ALGORITHM,
    )
    return encoded_jwt
