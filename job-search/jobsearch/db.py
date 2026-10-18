"""Engine and session helpers."""

from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Iterator

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from jobsearch import models  # noqa: F401  (registers tables)
from jobsearch.config import load_settings


def make_engine(db_path: Path | str) -> Engine:
    if str(db_path) != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return make_engine(load_settings().db_path)


@contextmanager
def session_scope(engine: Engine | None = None) -> Iterator[Session]:
    with Session(engine or get_engine(), expire_on_commit=False) as session:
        yield session
