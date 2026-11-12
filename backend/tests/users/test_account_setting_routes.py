from unittest.mock import MagicMock

import app.routers.user as user_router
from app.database import get_supabase


def test_get_payment_handles_defaults_to_null(authenticated_client, fake_db):
    fake_db.table.return_value.execute.return_value.data = []
    response = authenticated_client.get("/api/user/me/payment-handles")
    assert response.status_code == 200
    assert response.json() == {
        "venmo_handle": None,
        "zelle_identifier": None,
        "cash_app_handle": None,
    }


def test_patch_payment_handles_sends_explicit_null_and_omits_other_fields(
    authenticated_client, fake_db, user_session
):
    upsert = fake_db.table.return_value.upsert
    upsert.return_value.execute.return_value.data = [
        {
            "venmo_handle": None,
            "zelle_identifier": None,
            "cash_app_handle": "$testonly",
        }
    ]
    response = authenticated_client.patch(
        "/api/user/me/payment-handles",
        json={"venmo_handle": None},
    )
    assert response.status_code == 200
    assert response.json()["venmo_handle"] is None
    assert response.json()["cash_app_handle"] == "$testonly"
    upsert.assert_called_once_with(
        {"authid": user_session.auth_id, "venmo_handle": None},
        on_conflict="authid",
        default_to_null=False,
    )


def test_patch_payment_handles_rejects_client_supplied_authid(
    authenticated_client, fake_db
):
    response = authenticated_client.patch(
        "/api/user/me/payment-handles",
        json={"authid": "another-account"},
    )
    assert response.status_code == 422
    fake_db.table.assert_not_called()


def test_delete_account_uses_signed_in_users_auth_id(
    authenticated_client, user_session, monkeypatch
):
    admin_client = MagicMock()
    monkeypatch.setattr(
        user_router, "get_supabase_admin", MagicMock(return_value=admin_client)
    )
    response = authenticated_client.delete("/api/user/me")
    assert response.status_code == 204
    assert response.content == b""
    admin_client.auth.admin.delete_user.assert_called_once_with(
        user_session.auth_id,
        should_soft_delete=False,
    )


def test_delete_account_requires_authentication(client, monkeypatch):
    get_admin = MagicMock()
    monkeypatch.setattr(user_router, "get_supabase_admin", get_admin)
    response = client.delete("/api/user/me")
    assert response.status_code == 401
    get_admin.assert_not_called()


def test_public_profile_displays_deleted_user(client, fake_db, monkeypatch):
    monkeypatch.setitem(
        client.app.dependency_overrides, get_supabase, lambda: fake_db
    )
    fake_db.rpc.return_value.execute.return_value.data = [
        {"userid": 7, "name": "Deleted User", "location": None}
        ]
    response = client.get("/api/user/7")
    assert response.status_code == 200
    assert response.json() == {
        "userid": 7,
        "name": "Deleted User",
        "location": None,
    }
    fake_db.rpc.assert_called_once_with(
    "get_public_user_profile", {"p_userid": 7}
    )