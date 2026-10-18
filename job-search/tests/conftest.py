import pytest
from sqlmodel import Session

from jobsearch.db import make_engine


@pytest.fixture
def session(tmp_path):
    engine = make_engine(tmp_path / "test.db")
    with Session(engine, expire_on_commit=False) as s:
        yield s
