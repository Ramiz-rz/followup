import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEST_DB_FD, TEST_DB_PATH = tempfile.mkstemp(suffix=".db")
os.environ["FOLLOWUP_TEST_DB"] = TEST_DB_PATH

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.main import app
from app.database import get_db, Base
from fastapi.testclient import TestClient

engine = create_engine(f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    os.close(TEST_DB_FD)
    os.remove(TEST_DB_PATH)


@pytest.fixture
def client():
    return TestClient(app)
