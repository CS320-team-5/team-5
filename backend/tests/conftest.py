from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies.auth import AuthSession, get_auth_session
from app.main import app


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """Keep a test's mocked FastAPI dependencies out of other tests."""
    previous = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


@pytest.fixture
def client():
    """Exercise real routing and Pydantic validation without starting a server."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def fake_db():
    """A chainable fake PostgREST client; never calls Supabase."""
    db = MagicMock()
    query = db.table.return_value
    for method in ("select", "insert", "update", "delete", "eq", "neq",
                   "gt", "lte", "limit", "order"):
        getattr(query, method).return_value = query
    return db


@pytest.fixture
def user_session(fake_db):
    return AuthSession(
        db=fake_db,
        user_id=7,
        auth_id="test-auth-uuid",
        access_token="test-token",
    )


@pytest.fixture
def authenticated_client(client, user_session):
    app.dependency_overrides[get_auth_session] = lambda: user_session
    return client


@pytest.fixture
def user_row():
    return {"userid": 7, "name": "Test User", "location": "Amherst"}
