"""SQLAlchemy engine, session factory and declarative base."""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def normalize_db_url(url: str) -> str:
    """Hosting providers (Render, Railway, Heroku) give `postgres://...`; SQLAlchemy+psycopg3 needs this form."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def _make_engine(url: str):
    url = normalize_db_url(url)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True)


engine = _make_engine(get_settings().database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables. Good enough for the prototype (no migrations yet)."""
    from app import models  # noqa: F401  (registers models on Base.metadata)

    Base.metadata.create_all(bind=engine)
