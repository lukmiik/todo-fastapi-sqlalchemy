from typing import Annotated, Any, Generator

from fastapi import Depends
from sqlalchemy.orm.session import Session

from src.db.database import SessionLocal


def get_db() -> Generator[Session, Any, None]:
    """Yields sql alchemy session for dependency for fastapi to use.

    Yields:
        Generator[Session, Any, None]: yield session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_db)]
