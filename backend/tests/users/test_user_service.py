from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

import app.services.user as user_service
from app.models.user import UserUpdate


def test_get_user_uses_requested_id(monkeypatch, fake_db, user_row):
    get_user = MagicMock(return_value=user_row)
    monkeypatch.setattr(user_service.user_repository, "get_user", get_user)

    result = user_service.get_user(fake_db, 7)

    assert result.model_dump() == user_row
    get_user.assert_called_once_with(fake_db, 7)


def test_get_user_omits_authid(monkeypatch, fake_db, user_row):
    get_user = MagicMock(return_value={**user_row, "authid": "private"})
    monkeypatch.setattr(user_service.user_repository, "get_user", get_user)

    result = user_service.get_user(fake_db, 7)

    assert result.model_dump() == user_row
    get_user.assert_called_once_with(fake_db, 7)


def test_get_user_missing_returns_404(monkeypatch, fake_db):
    monkeypatch.setattr(
        user_service.user_repository,
        "get_user",
        lambda db, user_id: None,
    )

    with pytest.raises(HTTPException) as error:
        user_service.get_user(fake_db, 404)

    assert error.value.status_code == 404


def test_update_user_targets_requested_id(monkeypatch, user_session, user_row):
    update_user = MagicMock(return_value={**user_row, "name": "Changed"})
    monkeypatch.setattr(user_service.user_repository, "update_user", update_user)

    result = user_service.update_user(
        user_session.db,
        user_session.user_id,
        UserUpdate(name="Changed"),
    )

    assert result.name == "Changed"
    update_user.assert_called_once_with(user_session.db, 7, {"name": "Changed"})


def test_update_user_empty_patch_reads_profile(monkeypatch, fake_db, user_row):
    get_user = MagicMock(return_value=user_row)
    update_user = MagicMock()

    monkeypatch.setattr(user_service.user_repository, "get_user", get_user)
    monkeypatch.setattr(user_service.user_repository, "update_user", update_user)

    result = user_service.update_user(fake_db, 7, UserUpdate())

    assert result.model_dump() == user_row
    get_user.assert_called_once_with(fake_db, 7)
    update_user.assert_not_called()


def test_update_user_missing_returns_404(monkeypatch, fake_db):
    monkeypatch.setattr(
        user_service.user_repository,
        "update_user",
        lambda *args: None,
    )

    with pytest.raises(HTTPException) as error:
        user_service.update_user(fake_db, 7, UserUpdate(name="New"))

    assert error.value.status_code == 404


def test_schema_rejects_unauthorized_fields():
    with pytest.raises(ValidationError):
        UserUpdate(userid=12, name="Not Allowed")