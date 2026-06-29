import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.dependencies import get_db
from app.main import app

TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


VALID_SIGNUP = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass1",
    "first_name": "Test",
    "last_name": "User",
}

ADMIN_SIGNUP = {
    "username": "adminuser",
    "email": "admin@example.com",
    "password": "AdminPass1",
    "first_name": "Admin",
    "last_name": "User",
}


@pytest.fixture()
def registered_client(client):
    """Client with a signed-up user; cookies maintained automatically."""
    resp = client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    assert resp.status_code == 201, resp.json()
    return client


@pytest.fixture()
def access_token(registered_client):
    """Raw access token string extracted from cookie for Bearer-header tests."""
    return registered_client.cookies.get("access_token")


@pytest.fixture()
def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}
