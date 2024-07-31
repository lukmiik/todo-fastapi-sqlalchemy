from fastapi import FastAPI

from src.api.health.health import router

app = FastAPI()

app.include_router(router)
