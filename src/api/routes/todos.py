from typing import Any, TypeVar

from fastapi import APIRouter, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.customization import CustomizedPage, UseParamsFields
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from starlette import status
from starlette.responses import JSONResponse

from src.api.routes.auth import CurrentActiveUserDep
from src.api.schemas.todos import (
    TodosAllFields,
    TodosCreateIn,
    TodosWithoutUser,
    TodoUpdateIn,
)
from src.db.dependency import DbDep
from src.db.models import Todo

router = APIRouter(prefix="/todos", tags=["todo"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(
    db: DbDep,
    current_user: CurrentActiveUserDep,
    todo_in: TodosCreateIn,
) -> TodosAllFields:
    """Creates todo with for current_user.

    Args:
        db (DbDep): db dependency
        current_user (CurrentActiveUserDep): current user
        todo_in (TodosCreateIn): todo data

    Returns:
        TodosCreateOut: todo data
    """
    todo_data = todo_in.model_dump() | {"user": current_user.id}
    todo = Todo(**todo_data)

    db.add(todo)
    db.commit()

    todo_response = TodosAllFields(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        finished=todo.finished,
        user=todo.user,
    )

    return todo_response


T = TypeVar("T")

RegularPage = CustomizedPage[Page[T], UseParamsFields(size=20)]


# response model is enough to serialize the response you dont have to convert
# in the code
@router.get("/", response_model=RegularPage[TodosWithoutUser])
async def get_todos(db: DbDep, current_user: CurrentActiveUserDep) -> Any:
    """Get all todos of a current_user.

    Args:
        db (DbDep): db dependency
        current_user (CurrentActiveUserDep): current user

    Returns:
        Any: list of todos of current user
    """
    stmt = select(
        Todo.id, Todo.title, Todo.description, Todo.finished, Todo.user
    ).filter(Todo.user == current_user.id)

    return paginate(db, stmt)


@router.get("/{id}/", response_model=TodosWithoutUser)
async def get_todo(db: DbDep, current_user: CurrentActiveUserDep, id: int) -> Todo:
    """Gets todo by id.

    Args:
        db (DbDep): db dependency
        current_user (CurrentActiveUserDep): current user
        id (int): id of the todo

    Raises:
        HTTPException: todo not found in db
        HTTPException: todo is not of current user or admin

    Returns:
        Todo: TodosWithoutUser
    """
    todo = db.query(Todo).filter(Todo.id == id).one_or_none()

    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="todo not found"
        )

    if todo.user != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized."
        )

    return todo


@router.put("/{id}/", status_code=status.HTTP_200_OK, response_model=TodosWithoutUser)
async def update_todo(
    db: DbDep,
    current_user: CurrentActiveUserDep,
    id: int,
    todo_in: TodoUpdateIn,
) -> Todo:
    """Updates todo.

    Args:
        db (DbDep): db dependency
        current_user (CurrentActiveUserDep): current user
        id (int): todo it to update
        todo_in (TodoUpdateIn): todo data to update

    Raises:
        HTTPException: todo with provided id doesn't exist
        HTTPException: Not authorized current user is not an author of todo

    Returns:
        Todo: todo data without user
    """
    todo = db.query(Todo).filter(Todo.id == id).one_or_none()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized."
        )

    todo.title = todo_in.title
    todo.description = todo_in.description
    todo.finished = todo_in.finished

    db.commit()

    return todo


@router.delete("/{id}/")
async def delete_todo(
    db: DbDep, current_user: CurrentActiveUserDep, id: int
) -> JSONResponse:
    """Deletes todo.

    Args:
        db (DbDep): db dependency
        current_user (CurrentActiveUserDep): current user
        id (int): id of a todo to delete

    Raises:
        HTTPException: todo not found
        HTTPException: user unauthorized to delete a todo

    Returns:
        JSONResponse: 204 response with success message
    """
    todo = db.query(Todo).filter(Todo.id == id).one_or_none()

    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found."
        )

    if todo.user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized."
        )

    db.delete(todo)
    db.commit()

    return JSONResponse(
        content={"message": "Todo deleted successfully."},
        status_code=status.HTTP_204_NO_CONTENT,
    )
