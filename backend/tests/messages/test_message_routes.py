from unittest.mock import MagicMock

from app.routers import message as routes
from app.services.message import Message

ROW = {
    "messageid": 11, "cartid": 3, "userid": 7,
    "messagetext": "Hello", "timestamp": "2026-10-29T12:00:00+00:00",
}


def test_send(authenticated_client, user_session, monkeypatch):
    send = MagicMock(return_value=Message.model_validate(ROW))
    monkeypatch.setattr(routes.service, "create_cart_message", send)
    response = authenticated_client.post("/api/message/cart/3", json={"messagetext": "Hello"})
    assert response.status_code == 201
    assert response.json()["userid"] == 7
    assert send.call_args.args[0] is user_session


def test_reject_sender_override(authenticated_client, monkeypatch):
    send = MagicMock()
    monkeypatch.setattr(routes.service, "create_cart_message", send)
    response = authenticated_client.post("/api/message/cart/3", json={"messagetext": "hi", "userid": 1})
    assert response.status_code == 422
    send.assert_not_called()


def test_list(authenticated_client, monkeypatch):
    monkeypatch.setattr(routes.service, "get_cart_messages", lambda session, cid, limit: [Message.model_validate(ROW)])
    response = authenticated_client.get("/api/message/cart/3?limit=20")
    assert response.status_code == 200
    assert response.json()[0]["messagetext"] == "Hello"


def test_list_limit_validated(authenticated_client):
    assert authenticated_client.get("/api/message/cart/3?limit=101").status_code == 422


def test_update(authenticated_client, monkeypatch):
    monkeypatch.setattr(routes.service, "update_message", lambda session, mid, body: Message.model_validate({**ROW, "messagetext": body.messagetext}))
    response = authenticated_client.patch("/api/message/11", json={"messagetext": "Edited"})
    assert response.status_code == 200
    assert response.json()["messagetext"] == "Edited"


def test_delete(authenticated_client, monkeypatch):
    remove = MagicMock()
    monkeypatch.setattr(routes.service, "delete_message", remove)
    response = authenticated_client.delete("/api/message/11")
    assert response.status_code == 204
    remove.assert_called_once()


def test_auth_required(client):
    assert client.get("/api/message/cart/3").status_code == 401
    assert client.post("/api/message/cart/3", json={"messagetext": "Hi"}).status_code == 401
