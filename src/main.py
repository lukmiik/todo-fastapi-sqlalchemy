from fastapi import FastAPI

from src.api.routes import auth, health, users
from src.db.base import Base
from src.db.database import engine

app = FastAPI(title="todo fastapi sqlalchemy")

Base.metadata.create_all(engine)

app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)
