from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.message import MessageCreate
from app.services import message as service


def test_only_accessible_carts_are_returned(monkeypatch, user_session):
    expected = [{"cartid": 3, "owneruserid": 7, "status": "Active",
                 "deadline": "2026-12-01T00:00:00+00:00", "location": "Lobby",
                 "storeid": 2, "minimumamount": "50.00", "currentamount": "10.00"}]
    get_carts = MagicMock(return_value=expected)
    monkeypatch.setattr(service.repository, "list_message_carts", get_carts)
    assert [row.model_dump(mode="json") for row in service.get_message_carts(user_session)] == [
        {**expected[0], "notes": None}]
    get_carts.assert_called_once_with(user_session.db, 7)


@pytest.mark.parametrize("status,expired", [("Inactive", False), ("Active", True)])
def test_cannot_send_when_cart_closed(monkeypatch, user_session, status, expired):
    deadline = datetime.now(timezone.utc) + timedelta(days=-1 if expired else 1)
    monkeypatch.setattr(service.repository, "find_cart", lambda db, cid: {
        "owneruserid": 7, "status": status, "deadline": deadline.isoformat()
    })
    insert = MagicMock()
    monkeypatch.setattr(service.repository, "create_message", insert)
    with pytest.raises(HTTPException) as exc:
        service.create_cart_message(user_session, 3, MessageCreate(messagetext="Hello"))
    assert exc.value.status_code == 409
    insert.assert_not_called()
