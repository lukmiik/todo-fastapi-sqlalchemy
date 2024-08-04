from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.settings import Settings

engine = create_engine(
    Settings.get_settings().DB_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
