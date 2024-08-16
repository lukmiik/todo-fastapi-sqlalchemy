from sqlalchemy.orm import Session

from src.db.models import Todo, Users


async def create_todos_for_user(
    db: Session, todos_data: list[dict], user: Users
) -> None:
    todos = [Todo(**(todo | {"user": user.id})) for todo in todos_data]

    db.add_all(todos)
    db.commit()


async def create_todo_for_user(db: Session, todo_data: dict, user: Users) -> Todo:
    todo = Todo(**(todo_data | {"user": user.id}))

    db.add(todo)
    db.commit()

    return todo
