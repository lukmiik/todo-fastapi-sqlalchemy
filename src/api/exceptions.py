from fastapi import FastAPI, Request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.responses import JSONResponse

# https://github.com/fastapi/fastapi/issues/917


def add_custom_exception(app: FastAPI) -> None:
    """Adds custom exception created here to the app.

    Args:
        app (FastAPI): app
    """

    @app.exception_handler(IntegrityError)
    async def sqlalchemy_integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        """Custom sqlalchemy integrity error handler."""
        return JSONResponse(status_code=400, content={"detail": "db integrity error."})

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """Custom sqlalchemy error handler."""
        print("exc, ", exc)
        return JSONResponse(status_code=500, content={"detail": "db error occurred."})
