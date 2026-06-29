import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.dependencies import get_db
from app.core.rate_limit import limiter
from app.main import app

TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture(autouse=True)
def disable_rate_limit():
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    # SAVEPOINT so service-level commit() doesn't escape the outer transaction
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested
        if trans.nested and not trans._parent.nested:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


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
