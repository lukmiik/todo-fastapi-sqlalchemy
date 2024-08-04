from fastapi import FastAPI

from src.api import health, users
from src.db.base import Base
from src.db.database import engine

app = FastAPI()

Base.metadata.create_all(engine)

app.include_router(health.router)
app.include_router(users.router)
