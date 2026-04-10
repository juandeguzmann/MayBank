from collections.abc import Generator

from sqlalchemy.orm import Session

from backend.db.postgres import session_factory


def get_session() -> Generator[Session, None, None]:
    with session_factory() as session:
        yield session
