from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.message import MessageCreate, MessageUpdate
from app.services import message as service


ROW = {
    "messageid": 11, "cartid": 3, "userid": 7,
    "messagetext": "Hello", "timestamp": "2026-10-29T12:00:00+00:00",
}


def test_owner_can_send(monkeypatch, user_session):
    monkeypatch.setattr(service.repository, "find_cart", lambda db, cid: {"owneruserid": 7})
    create = MagicMock(return_value=ROW)
    monkeypatch.setattr(service.repository, "create_message", create)
    result = service.create_cart_message(user_session, 3, MessageCreate(messagetext="Hello"))
    assert result.messageid == 11
    create.assert_called_once_with(user_session.db, 3, 7, "Hello")


def test_active_participant_can_read(monkeypatch, user_session):
    monkeypatch.setattr(service.repository, "find_cart", lambda db, cid: {"owneruserid": 6})
    monkeypatch.setattr(service.repository, "find_active_participant", lambda db, cid, uid: True)
    monkeypatch.setattr(service.repository, "list_cart_messages", lambda db, cid, limit: [ROW])
    assert service.get_cart_messages(user_session, 3, 50)[0].messageid == 11


def test_nonmember_cannot_read(monkeypatch, user_session):
    monkeypatch.setattr(service.repository, "find_cart", lambda db, cid: {"owneruserid": 6})
    monkeypatch.setattr(service.repository, "find_active_participant", lambda db, cid, uid: False)
    with pytest.raises(HTTPException) as e:
        service.get_cart_messages(user_session, 3, 50)
    assert e.value.status_code == 403


def test_missing_cart(monkeypatch, user_session):
    monkeypatch.setattr(service.repository, "find_cart", lambda db, cid: None)
    with pytest.raises(HTTPException) as e:
        service.get_cart_messages(user_session, 3, 50)
    assert e.value.status_code == 404


def test_cannot_edit_other_user_message(monkeypatch, user_session):
    monkeypatch.setattr(service.repository, "find_message", lambda db, mid: {**ROW, "userid": 6})
    monkeypatch.setattr(service.repository, "find_cart", lambda db, cid: {"owneruserid": 7})
    with pytest.raises(HTTPException) as e:
        service.update_message(user_session, 11, MessageUpdate(messagetext="Changed"))
    assert e.value.status_code == 403


def test_own_edit_updates_only_message_text(monkeypatch, user_session):
    monkeypatch.setattr(service.repository, "find_message", lambda db, mid: ROW)
    monkeypatch.setattr(service.repository, "find_cart", lambda db, cid: {"owneruserid": 7})
    update = MagicMock(return_value={**ROW, "messagetext": "Changed"})
    monkeypatch.setattr(service.repository, "update_message", update)
    assert service.update_message(user_session, 11, MessageUpdate(messagetext="Changed")).messagetext == "Changed"
    update.assert_called_once_with(user_session.db, 11, 7, "Changed")


def test_own_delete(monkeypatch, user_session):
    monkeypatch.setattr(service.repository, "find_message", lambda db, mid: ROW)
    monkeypatch.setattr(service.repository, "find_cart", lambda db, cid: {"owneruserid": 7})
    delete = MagicMock(return_value=True)
    monkeypatch.setattr(service.repository, "delete_message", delete)
    service.delete_message(user_session, 11)
    delete.assert_called_once_with(user_session.db, 11, 7)
