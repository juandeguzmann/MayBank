from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel
import backend.config as config

_dsn = (
    f"postgresql+psycopg2://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}"
    f"@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
)

engine = create_engine(_dsn, pool_size=5, max_overflow=10)
session_factory: sessionmaker[Session] = sessionmaker(engine, expire_on_commit=False)


def create_tables() -> None:
    import backend.db.models.postgres  # noqa: F401 — registers models with SQLModel metadata
    SQLModel.metadata.create_all(engine)


def close_engine() -> None:
    engine.dispose()
