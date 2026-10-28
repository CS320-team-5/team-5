from unittest.mock import MagicMock

import app.routers.user as user_router
from app.database import get_supabase
from app.main import app


def test_get_current_user(authenticated_client, user_session, user_row, monkeypatch):
    get_user = MagicMock(return_value={**user_row, "authid": "not-public"})
    monkeypatch.setattr(user_router.user_service, "get_user", get_user)

    response = authenticated_client.get("/api/user/me")

    assert response.status_code == 200
    assert response.json() == user_row
    get_user.assert_called_once_with(user_session.db, user_session.user_id)


def test_get_user(client, fake_db, monkeypatch):
    app.dependency_overrides[get_supabase] = lambda: fake_db
    get_user = MagicMock(return_value={
        "userid": 12,
        "name": "Other User",
        "location": "Boston",
        "authid": "should-not-leak",
    })
    monkeypatch.setattr(user_router.user_service, "get_user", get_user)

    response = client.get("/api/user/12")

    assert response.status_code == 200
    assert response.json() == {
        "userid": 12,
        "name": "Other User",
        "location": "Boston",
    }
    get_user.assert_called_once_with(fake_db, 12)


def test_update_current_user_uses_authenticated_session(
    authenticated_client, user_session, monkeypatch
):
    update_user = MagicMock(return_value={
        "userid": 7,
        "name": "New Name",
        "location": "Boston",
    })
    monkeypatch.setattr(user_router.user_service, "update_user", update_user)

    response = authenticated_client.patch(
        "/api/user/me",
        json={"name": "New Name", "location": "Boston"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"

    db_arg, user_id_arg, body_arg = update_user.call_args.args
    assert db_arg is user_session.db
    assert user_id_arg == user_session.user_id
    assert body_arg.model_dump(exclude_unset=True) == {
        "name": "New Name",
        "location": "Boston",
    }


def test_update_current_user_rejects_userid(authenticated_client, monkeypatch):
    update_user = MagicMock()
    monkeypatch.setattr(user_router.user_service, "update_user", update_user)

    response = authenticated_client.patch(
        "/api/user/me",
        json={"userid": 12, "name": "Imposter"},
    )

    assert response.status_code == 422
    update_user.assert_not_called()


def test_get_current_user_requires_auth(client):
    response = client.get("/api/user/me")
    assert response.status_code == 401


def test_get_user_requires_positive_id(client, fake_db):
    app.dependency_overrides[get_supabase] = lambda: fake_db

    response = client.get("/api/user/0")

    assert response.status_code == 422