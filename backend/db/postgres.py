from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel
import backend.config as config

_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        dsn = (
            f"postgresql+psycopg2://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}"
            f"@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
        )
        _engine = create_engine(dsn, pool_size=5, max_overflow=10)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


def create_tables() -> None:
    import backend.db.models.postgres  # noqa: F401 — registers models with SQLModel metadata
    SQLModel.metadata.create_all(get_engine())


def close_engine() -> None:
    global _engine, _session_factory
    if _engine:
        _engine.dispose()
        _engine = None
        _session_factory = None
