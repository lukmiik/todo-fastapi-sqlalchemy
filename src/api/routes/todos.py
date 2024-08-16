from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse

from src.api.routes.auth import get_current_active_user
from src.db.dependency import DbDep
from src.db.models import Todo, Users

router = APIRouter(prefix="/todos", tags=["todo"])


class TodosCreateIn(BaseModel):
    """Model for todos create request."""

    title: str
    description: str | None = None


class TodosAllFields(BaseModel):
    """Model for todos create response."""

    id: int
    title: str
    description: str | None
    finished: bool
    user: int


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(
    db: DbDep,
    current_user: Annotated[Users, Depends(get_current_active_user)],
    todo_in: TodosCreateIn,
) -> TodosAllFields:
    """Creates todo with for current_user.

    Args:
        db (DbDep): db dependency
        current_user (Annotated[Users, Depends): current user
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


class TodosWithoutUser(BaseModel):
    """Todos model without user."""

    id: int
    title: str
    description: str | None
    finished: bool


# response model is enough to serialize the response you dont have to convert
# in the code
@router.get("/", response_model=list[TodosWithoutUser])
async def get_todos(
    db: DbDep, current_user: Annotated[Users, Depends(get_current_active_user)]
) -> list[dict[str, int | str | bool | Users]]:
    """Get all todos of a current_user.

    Args:
        db (DbDep): db dependency
        current_user (Annotated[Users, Depends): current user

    Returns:
        list[Todo]: list of todos of current user
    """
    todos = (
        db.query(Todo.id, Todo.title, Todo.description, Todo.finished, Todo.user)
        .filter(Todo.user == current_user.id)
        .all()
    )
    todos_dict = [todo._asdict() for todo in todos]

    return todos_dict


@router.get("/{id}/", response_model=TodosWithoutUser)
async def get_todo(
    db: DbDep, current_user: Annotated[Users, Depends(get_current_active_user)], id: int
) -> Todo:
    """Gets todo by id.

    Args:
        db (DbDep): db dependency
        current_user (Annotated[Users, Depends): current user
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


class TodoUpdateIn(BaseModel):
    """Model for updating todo."""

    title: str
    description: str | None
    finished: bool


@router.put("/{id}/", status_code=status.HTTP_200_OK, response_model=TodosWithoutUser)
async def update_todo(
    db: DbDep,
    current_user: Annotated[Users, Depends(get_current_active_user)],
    id: int,
    todo_in: TodoUpdateIn,
) -> Todo:
    """Updates todo.

    Args:
        db (DbDep): db dependency
        current_user (Annotated[Users, Depends): current user
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
    db: DbDep, current_user: Annotated[Users, Depends(get_current_active_user)], id: int
) -> JSONResponse:
    """Deletes todo.

    Args:
        db (DbDep): db dependency
        current_user (Annotated[Users, Depends): current user
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
