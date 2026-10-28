from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import app.user as user_module
from backend.app.dependencies.auth import get_auth_session
from app.database import get_supabase
from app.main import app


client = TestClient(app)


def make_session(user_id: int = 7):
    return SimpleNamespace(
        db=MagicMock(),
        user_id=user_id,
        auth_id=f"fake-auth-id-{user_id}",
        access_token="fake-token",
    )


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()


def test_get_me(monkeypatch):
    session = make_session(7)

    app.dependency_overrides[get_auth_session] = lambda: session

    monkeypatch.setattr(
        user_module,
        "find_user",
        lambda db, user_id: {
            "userid": 7,
            "authid": "private-auth-id",
            "name": "Vince",
            "location": "Amherst",
        },
    )

    response = client.get("/api/user/me")

    assert response.status_code == 200
    assert response.json()["userid"] == 7
    assert "authid" not in response.json()


def test_get_user(monkeypatch):
    db = MagicMock()

    app.dependency_overrides[get_supabase] = lambda: db

    monkeypatch.setattr(
        user_module,
        "find_user",
        lambda database, user_id: {
            "userid": user_id,
            "authid": "private-auth-id",
            "name": "Robert",
            "location": "Boston",
        },
    )

    response = client.get("/api/user/12")

    assert response.status_code == 200
    assert response.json()["userid"] == 12
    assert "authid" not in response.json()


def test_update_me(monkeypatch):
    session = make_session(7)

    app.dependency_overrides[get_auth_session] = lambda: session

    table = session.db.table.return_value
    table.update.return_value = table
    table.eq.return_value = table
    table.select.return_value = table

    monkeypatch.setattr(
        user_module,
        "execute_query",
        lambda query: [
            {
                "userid": 7,
                "authid": "private-auth-id",
                "name": "New Name",
                "location": "Boston",
            }
        ],
    )

    response = client.patch(
        "/api/user/me",
        json={
            "name": "New Name",
            "location": "Boston",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"

    # Confirms we update the authenticated user, not a caller-supplied user.
    table.eq.assert_called_once_with("userid", 7)


def test_cannot_change_userid():
    session = make_session(7)

    app.dependency_overrides[get_auth_session] = lambda: session

    response = client.patch(
        "/api/user/me",
        json={
            "userid": 12,
            "name": "Fake User",
        },
    )

    assert response.status_code == 422