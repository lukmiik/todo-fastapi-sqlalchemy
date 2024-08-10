from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status

from src.api.schemas.auth import (
    AuthUserIn,
    RefreshTokenRequest,
    Token,
    TokenData,
    TokenDataIn,
)
from src.db.dependency import DbDep
from src.db.models import Users
from src.settings import Settings

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

CREDENTIALS_EXCEPTION: HTTPException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def authenticate_user(db: DbDep, user_data: AuthUserIn) -> Users:
    """Checks if user with given credentials exists.

    Args:
        db (DbDep): db session
        user_data (AuthUserIn): user data for authentication

    Returns:
        Users: User instance
    """
    user = db.query(Users).filter(Users.username == user_data.username).one_or_none()
    if user is None or user.password != user_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_access_token(data: TokenDataIn) -> str:
    """Creates access token.

    Args:
        data (TokenDataIn): user data for creating token

    Returns:
        str: encoded jwt access token
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=Settings.get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = data.model_dump() | {"exp": expire}
    encoded_jwt = jwt.encode(
        to_encode,
        Settings.get_settings().SECRET_KEY,
        algorithm=Settings.get_settings().ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(data: TokenDataIn) -> str:
    """Creates refresh token.

    Args:
        data (TokenDataIn): user data for creating token

    Returns:
        str: encoded refresh token
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=Settings.get_settings().REFRESH_TOKEN_EXPIRE_MINUTES
    )
    to_encode = data.model_dump() | {"exp": expire}
    encoded_jwt = jwt.encode(
        to_encode,
        Settings.get_settings().REFRESH_SECRET_KEY,
        Settings.get_settings().ALGORITHM,
    )
    return encoded_jwt


async def get_current_user(
    db: DbDep, token: Annotated[str, Depends(oauth2_scheme)]
) -> Users:
    """Returns current user from jwt token.

    Args:
        db (DbDep): db session
        token (Annotated[str, Depends): access token

    Raises:
        CREDENTIALS_EXCEPTION: invalid credentials

    Returns:
        Users: currently logged in user
    """
    try:
        payload = jwt.decode(
            token,
            Settings.get_settings().SECRET_KEY,
            algorithms=[Settings.get_settings().ALGORITHM],
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise CREDENTIALS_EXCEPTION
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid access token") from e
    user = db.query(Users).filter(Users.username == token_data.username).one_or_none()
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


async def get_current_active_user(
    current_user: Annotated[Users, Depends(get_current_user)],
) -> Users:
    """Checks if current user is active.

    Args:
        current_user (Annotated[Users, Depends): current user

    Raises:
        HTTPException: user not active

    Returns:
        Users: current user
    """
    if current_user.is_active:
        return current_user
    raise HTTPException(status_code=400, detail="Inactive User")


@router.post("/token/", status_code=status.HTTP_200_OK)
async def login(
    db: DbDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """Checks if user with given username and password exists and returns access token.

    Args:
        db (DbDep): db session
        form_data (Annotated[OAuth2PasswordRequestForm, Depends): given user data

    Returns:
        Token: access token and token type
    """
    user_data = AuthUserIn(username=form_data.username, password=form_data.password)
    user = authenticate_user(db, user_data)

    token_user_data = TokenDataIn(sub=user.username)

    access_token = create_access_token(token_user_data)
    refresh_token = create_refresh_token(token_user_data)

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/token/refresh/")
async def refresh(refresh_token: RefreshTokenRequest) -> Token:
    """Refreshed token.

    Args:
        refresh_token (TokenRefreshRequest): refresh token

    Raises:
        CREDENTIALS_EXCEPTION: Invalid credentials

    Returns:
        Token: new access and refresh token
    """
    try:
        payload = jwt.decode(
            refresh_token.refresh_token,
            Settings.get_settings().REFRESH_SECRET_KEY,
            algorithms=[Settings.get_settings().ALGORITHM],
        )
    except jwt.InvalidTokenError as e:
        raise CREDENTIALS_EXCEPTION from e
    username: str | None = payload.get("sub")
    if username is None:
        raise CREDENTIALS_EXCEPTION

    token_user_data = TokenDataIn(sub=username)

    new_access_token = create_access_token(token_user_data)
    new_refresh_token = create_refresh_token(token_user_data)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )
