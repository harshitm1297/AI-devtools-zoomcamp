import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


DEFAULT_DATABASE_URL = "sqlite:///./sprintlane.db"


def create_database_engine(database_url: str | None = None):
    """Create an engine without relying on SQLite-only SQL features."""
    url = database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    options: dict = {}
    if url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
        if url in {"sqlite://", "sqlite:///:memory:"}:
            options["poolclass"] = StaticPool
    return create_engine(url, **options)


def create_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
