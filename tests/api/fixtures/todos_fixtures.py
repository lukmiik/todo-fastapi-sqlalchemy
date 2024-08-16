import pytest
from sqlalchemy.orm import Session

from src.db.models import Todo, Users


@pytest.fixture
async def create_todo_in() -> dict:
    return {"title": "test_title", "description": "test_description"}


@pytest.fixture
async def create_todo_out() -> dict:
    return {
        "id": 1,
        "title": "test_title",
        "description": "test_description",
        "finished": False,
    }


@pytest.fixture
async def todos_to_create() -> list[dict]:
    todos = []
    for i in range(5):
        todos.append(
            {
                "id": i,
                "title": f"test_title{i}",
                "description": f"test_description{i}",
                "finished": bool(i % 2 == 0),
            }
        )

    return todos


@pytest.fixture
async def create_todos_and_user_in_db(db_session: Session) -> list[dict]:
    user_data: dict = {
        "id": 9999,
        "first_name": "test_first_name_for_todos",
        "last_name": "test_last_name_for_todos",
        "username": "test_username_for_todos",
        "email": "test@email.com_for_todos",
        "is_active": True,
        "role": "admin",
    }
    Users(**user_data)

    todos_data = []
    for i in range(5, 10):
        todos_data.append(
            {
                "id": i,
                "title": f"test_title{i}",
                "description": f"test_description{i}",
                "finished": bool(i % 2 == 0),
                "user": 9999,
            }
        )
    todos = [Todo(**todo_data) for todo_data in todos_data]

    db_session.add_all(todos)
    db_session.commit()

    return todos_data


@pytest.fixture
async def create_todo() -> dict:
    return {
        "id": 1,
        "title": "test_title",
        "description": "test_description",
        "finished": False,
    }


@pytest.fixture
async def update_todo() -> dict:
    return {
        "title": "test_update_title",
        "description": "test_update_description",
        "finished": True,
    }
