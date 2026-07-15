"""
Shared fixtures for API-level (Module 5) tests. Each test gets a fresh
in-memory SQLite DB via a dependency override on get_db — tests never
touch the real arogent.db file and never leak state between each other.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


@pytest.fixture
def db_session():
    # StaticPool forces a single shared connection for this in-memory DB —
    # without it, TestClient's requests (which can run on a different
    # thread than this fixture) would each get their own separate,
    # table-less in-memory database, since SQLite's :memory: is
    # connection-scoped, not just engine-scoped.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db_session: Session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # fixture owns closing the session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register_and_login(client: TestClient, username: str, role: str, assigned_village: str | None = None) -> str:
    """Helper: registers a user and returns a bearer token for them."""
    client.post("/api/v1/auth/register", json={
        "full_name": f"Test {username}",
        "username": username,
        "password": "pass123",
        "role": role,
        "assigned_village": assigned_village,
    })
    response = client.post("/api/v1/auth/login", data={"username": username, "password": "pass123"})
    return response.json()["access_token"]
