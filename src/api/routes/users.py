from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src.api.permissions import IsAdminDep
from src.api.routes.auth import CurrentActiveUserDep
from src.api.schemas.users import (
    ChangePasswordRequest,
    UserCreateRequest,
    UserCreateResponse,
    UserMeOut,
)
from src.db.dependency import DbDep
from src.db.models import Users

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/create/", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(db: DbDep, user_request: UserCreateRequest) -> UserCreateResponse:
    """Creates user and returns the user data without a password.

    Args:
        db (DbDep): db dependency
        user_request (UserCreateRequest): user request data

    Raises:
        HTTPException: 400 when db integrity errors
        HTTPException: 500 when db other db errors

    Returns:
        UserCreateResponse: returns created user data without password
    """
    user = Users(**user_request.model_dump())

    db.add(user)
    db.commit()

    user_response = UserCreateResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
    )
    return user_response


@router.post("/change_password/")
async def change_password(db: DbDep, request: ChangePasswordRequest) -> JSONResponse:
    """Allows user to change password.

    User provides username, current password and new password and method validates it.
    """
    user = db.query(Users).filter(Users.username == request.username).one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404, detail="User with given username not found."
        )

    if user.password != request.password:
        raise HTTPException(
            status_code=400,
            detail="Provided current password is incorrect.",
        )

    user.password = request.new_password
    db.commit()

    return JSONResponse(
        status_code=200, content={"detail": "Password successfully changed"}
    )


@router.get("/", response_model=list[UserCreateResponse])
async def get_all_users(db: DbDep, current_user: IsAdminDep) -> list[Users]:
    """Temporary endpoint for development. Move it to admin when implemented."""
    return db.query(Users).all()


@router.get("/me/")
async def me(
    current_user: CurrentActiveUserDep,
) -> UserMeOut:
    """Endpoint for retrieving data about current user.

    Args:
        current_user (CurrentActiveUserDep): current_user

    Returns:
        UserMeOut: user info
    """
    user = UserMeOut(
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
    )
    return user
