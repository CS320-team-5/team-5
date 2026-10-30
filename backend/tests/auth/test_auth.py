from types import SimpleNamespace
from unittest.mock import MagicMock

import app.dependencies.auth as auth_dependency


def test_missing_bearer_header_returns_401(client):
    response = client.get("/auth/test")
    assert response.status_code == 401


def test_wrong_auth_scheme_returns_401(client):
    response = client.get(
        "/auth/test", headers={"Authorization": "Basic credentials"}
    )
    assert response.status_code == 401


def test_valid_token_resolves_cocart_user(client, monkeypatch, fake_db):
    supabase = MagicMock()
    supabase.auth.get_user.return_value = SimpleNamespace(
        user=SimpleNamespace(id="auth-uuid-7")
    )
    fake_db.table.return_value.execute.return_value.data = [{"userid": 7}]
    monkeypatch.setattr(auth_dependency, "get_supabase", lambda: supabase)
    monkeypatch.setattr(auth_dependency, "get_user_supabase", lambda token: fake_db)

    response = client.get(
        "/auth/test", headers={"Authorization": "Bearer token-for-testing"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "authenticated": True, "auth_id": "auth-uuid-7", "user_id": 7
    }
    supabase.auth.get_user.assert_called_once_with("token-for-testing")
    fake_db.table.return_value.eq.assert_called_once_with("authid", "auth-uuid-7")


def test_valid_token_with_no_cocart_profile_returns_403(
    client, monkeypatch, fake_db
):
    supabase = MagicMock()
    supabase.auth.get_user.return_value = SimpleNamespace(
        user=SimpleNamespace(id="not-in-users-table")
    )
    fake_db.table.return_value.execute.return_value.data = []
    monkeypatch.setattr(auth_dependency, "get_supabase", lambda: supabase)
    monkeypatch.setattr(auth_dependency, "get_user_supabase", lambda token: fake_db)

    response = client.get(
        "/auth/test", headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 403
