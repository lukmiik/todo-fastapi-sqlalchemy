import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.db.models import Todo, Users
from tests.api.utils.todos import create_todo_for_user, create_todos_for_user

pytest_plugins: list[str] = [
    "tests.api.fixtures.todos_fixtures",
    "tests.api.fixtures.users_fixtures",
]

pytestmark = pytest.mark.anyio


async def test_create_todo(
    auth_user_async_test_client: tuple[AsyncClient, Users],
    create_todo_in: dict,
    create_todo_out: dict,
) -> None:
    client, user = auth_user_async_test_client
    create_todo_out["user"] = user.id

    response = await client.post("/todos/", json=create_todo_in)

    assert response.status_code == 201
    assert response.json() == create_todo_out


async def test_create_todo_not_authenticated(
    async_test_client: AsyncClient, create_todo_in: dict
) -> None:
    response = await async_test_client.post("/todos/", json=create_todo_in)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


async def test_get_todos(
    db_session: Session,
    auth_user_async_test_client: tuple[AsyncClient, Users],
    todos_to_create: list[dict],
    create_todos_and_user_in_db: list[Todo],
) -> None:
    """create_todos_and_user_in_db creates todos for different user to
    test if get_todos endpoint get only todos for current_user

    Args:
        db_session (Session): db session
        auth_user_async_test_client (tuple[AsyncClient, Users]): authenticated
        user and async client
        todos_to_create (list[dict]): todos data to create with current user
        create_todos_and_user_in_db (list[Todo]): creates todos for different
        user than current
    """
    client, user = auth_user_async_test_client
    await create_todos_for_user(db=db_session, todos_data=todos_to_create, user=user)

    response = await client.get("/todos/")

    assert response.status_code == 200
    assert response.json() == todos_to_create


async def test_get_todos_not_authenticated(
    async_test_client: AsyncClient, todos_to_create: list[dict]
) -> None:
    response = await async_test_client.get("/todos/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


async def test_get_todo(
    db_session: Session,
    auth_user_async_test_client: tuple[AsyncClient, Users],
    create_todo: dict,
) -> None:
    client, user = auth_user_async_test_client
    todo = await create_todo_for_user(db=db_session, todo_data=create_todo, user=user)

    response = await client.get(f"/todos/{todo.id}/")

    assert response.status_code == 200
    assert response.json() == create_todo


async def test_get_todo_not_authenticated(async_test_client: AsyncClient) -> None:
    response = await async_test_client.get("/todos/1/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


async def test_get_todo_admin(
    db_session: Session,
    auth_admin_async_test_client: tuple[AsyncClient, Users],
    create_todo: dict,
    create_user_in_db: Users,
) -> None:
    client, admin_user = auth_admin_async_test_client
    todo = await create_todo_for_user(
        db=db_session, todo_data=create_todo, user=create_user_in_db
    )

    response = await client.get(f"/todos/{todo.id}/")

    assert response.status_code == 200
    assert response.json() == create_todo


async def test_get_todo_not_found(
    auth_user_async_test_client: tuple[AsyncClient, Users],
) -> None:
    client, user = auth_user_async_test_client

    response = await client.get("/todos/5555/")

    assert response.status_code == 404
    assert response.json() == {"detail": "todo not found"}


async def test_get_todo_user_not_author(
    db_session: Session,
    auth_user_async_test_client: tuple[AsyncClient, Users],
    create_todo: dict,
    create_user_in_db: Users,
) -> None:
    client, user = auth_user_async_test_client
    todo = await create_todo_for_user(
        db=db_session, todo_data=create_todo, user=create_user_in_db
    )

    response = await client.get(f"/todos/{todo.id}/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authorized."}


async def test_update_todo(
    db_session: Session,
    auth_user_async_test_client: tuple[AsyncClient, Users],
    create_todo: dict,
    update_todo: dict,
) -> None:
    client, user = auth_user_async_test_client
    todo = await create_todo_for_user(db=db_session, todo_data=create_todo, user=user)

    response = await client.put(f"/todos/{todo.id}/", json=update_todo)

    expected_response = update_todo | {"id": todo.id}

    assert response.status_code == 200
    assert response.json() == expected_response


async def test_update_todo_not_found(
    auth_user_async_test_client: tuple[AsyncClient, Users],
    update_todo: dict,
) -> None:
    client, user = auth_user_async_test_client

    response = await client.put("/todos/5555/", json=update_todo)

    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


async def test_update_todo_not_author(
    db_session: Session,
    auth_user_async_test_client: tuple[AsyncClient, Users],
    create_todo: dict,
    create_user_in_db: Users,
    update_todo: dict,
) -> None:
    client, user = auth_user_async_test_client
    todo = await create_todo_for_user(
        db=db_session, todo_data=create_todo, user=create_user_in_db
    )

    response = await client.put(f"/todos/{todo.id}/", json=update_todo)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authorized."}


async def test_delete_todo(
    db_session: Session,
    auth_user_async_test_client: tuple[AsyncClient, Users],
    create_todo: dict,
) -> None:
    client, user = auth_user_async_test_client
    todo = await create_todo_for_user(db=db_session, todo_data=create_todo, user=user)

    assert db_session.query(Todo).filter(Todo.id == todo.id).one_or_none() is not None

    response = await client.delete(f"/todos/{todo.id}/")

    assert response.status_code == 204
    assert response.json() == {"message": "Todo deleted successfully."}
    assert db_session.query(Todo).filter(Todo.id == todo.id).one_or_none() is None


async def test_delete_todo_not_author(
    db_session: Session,
    auth_user_async_test_client: tuple[AsyncClient, Users],
    create_todo: dict,
    create_user_in_db: Users,
) -> None:
    client, user = auth_user_async_test_client
    todo = await create_todo_for_user(
        db=db_session, todo_data=create_todo, user=create_user_in_db
    )

    response = await client.delete(f"/todos/{todo.id}/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized."}


async def test_delete_todo_not_found(
    auth_user_async_test_client: tuple[AsyncClient, Users],
) -> None:
    client, user = auth_user_async_test_client

    response = await client.delete("/todos/5555/")

    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found."}
