from fastapi import FastAPI
from fastapi_pagination import add_pagination

from src.api.exceptions import add_custom_exception
from src.api.routes import auth, health, todos, users
from src.db.base import Base
from src.db.database import engine

app = FastAPI(title="todo fastapi sqlalchemy")

Base.metadata.create_all(engine)

app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)

add_custom_exception(app)

add_pagination(app)
