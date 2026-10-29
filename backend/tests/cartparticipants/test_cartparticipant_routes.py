from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.main import app
from app.dependencies.auth import get_auth_session
import app.routers.cartparticipant as participant_router


# Checks that the registered endpoint returns the service's participants.
def test_get_participants_route(
    monkeypatch, authenticated_client, user_session
):
    rows = [{
        "cartid": 1,
        "userid": 2,
        "status": "Active",
        "amountcontributed": "10.50",
        "joindate": "2026-10-28",
    }]

    lookup = MagicMock(return_value=rows)
    monkeypatch.setattr(
        participant_router.participant_service,
        "get_active_participants",
        lookup,
    )

    response = authenticated_client.get("/api/cart/1/participants")

    assert response.status_code == 200
    assert response.json()[0]["userid"] == 2
    lookup.assert_called_once_with(
        cart_id=1,
        session=user_session,
    )


# Checks that invalid cart IDs are rejected before calling the service.
@pytest.mark.parametrize("cart_id", ["0", "-1", "abc"])
def test_get_participants_rejects_invalid_id(
    monkeypatch, authenticated_client, cart_id
):
    lookup = MagicMock()
    monkeypatch.setattr(
        participant_router.participant_service,
        "get_active_participants",
        lookup,
    )

    response = authenticated_client.get(
        f"/api/cart/{cart_id}/participants"
    )

    assert response.status_code == 422
    lookup.assert_not_called()


# Checks that a request without login is rejected.
def test_get_participants_requires_login(monkeypatch, client):
    app.dependency_overrides.pop(get_auth_session, None)

    lookup = MagicMock()
    monkeypatch.setattr(
        participant_router.participant_service,
        "get_active_participants",
        lookup,
    )

    response = client.get("/api/cart/1/participants")

    assert response.status_code == 401
    lookup.assert_not_called()

# Checks that a valid join request reaches the service.
def test_join_cart_route(
    monkeypatch, authenticated_client, user_session
):
    row = {
        "cartid": 1,
        "userid": user_session.user_id,
        "status": "Active",
        "amountcontributed": "10.50",
        "joindate": "2026-10-28",
    }
    join = MagicMock(return_value=row)
    monkeypatch.setattr(
        participant_router.participant_service,
        "join_cart",
        join,
    )
    response = authenticated_client.post(
        "/api/cart/1/participants",
        json={"amountcontributed": "10.50"},
    )
    assert response.status_code == 201
    assert response.json()["userid"] == user_session.user_id
    arguments = join.call_args.kwargs
    assert arguments["cart_id"] == 1
    assert arguments["session"] is user_session
    assert str(arguments["body"].amountcontributed) == "10.50"


# Checks that invalid amounts and caller-supplied user IDs are rejected.
@pytest.mark.parametrize("body", [
    {"amountcontributed": "-1.00"},
    {"amountcontributed": "10.555"},
    {"amountcontributed": "10.00", "userid": 99},
])
def test_join_cart_rejects_invalid_body(
    monkeypatch, authenticated_client, body
):
    join = MagicMock()
    monkeypatch.setattr(
        participant_router.participant_service,
        "join_cart",
        join,
    )
    response = authenticated_client.post(
        "/api/cart/1/participants",
        json=body,
    )
    assert response.status_code == 422
    join.assert_not_called()

# Checks that a valid contribution update reaches the service.
def test_update_contribution_route(
    monkeypatch, authenticated_client, user_session
):
    row = {
        "cartid": 1,
        "userid": user_session.user_id,
        "status": "Active",
        "amountcontributed": "20.00",
        "joindate": "2026-10-28",
    }
    update = MagicMock(return_value=row)
    monkeypatch.setattr(
        participant_router.participant_service,
        "update_contribution",
        update,
    )
    response = authenticated_client.patch(
        "/api/cart/1/participants/me",
        json={"amountcontributed": "20.00"},
    )
    assert response.status_code == 200
    assert response.json()["userid"] == user_session.user_id
    arguments = update.call_args.kwargs
    assert arguments["cart_id"] == 1
    assert arguments["session"] is user_session
    assert str(arguments["body"].amountcontributed) == "20.00"


# Checks that invalid amounts and another user's ID are rejected.
@pytest.mark.parametrize("body", [
    {},
    {"amountcontributed": "-1.00"},
    {"amountcontributed": "10.555"},
    {"amountcontributed": "20.00", "userid": 99},
])
def test_update_contribution_rejects_invalid_body(
    monkeypatch, authenticated_client, body
):
    update = MagicMock()
    monkeypatch.setattr(
        participant_router.participant_service,
        "update_contribution",
        update,
    )
    response = authenticated_client.patch(
        "/api/cart/1/participants/me",
        json=body,
    )
    assert response.status_code == 422
    update.assert_not_called()


# Checks that expired-cart conflicts reach the caller.
def test_update_contribution_returns_conflict(
    monkeypatch, authenticated_client
):
    monkeypatch.setattr(
        participant_router.participant_service,
        "update_contribution",
        MagicMock(side_effect=HTTPException(409, "Cart has expired")),
    )
    response = authenticated_client.patch(
        "/api/cart/1/participants/me",
        json={"amountcontributed": "20.00"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Cart has expired"


# Checks that updating a contribution requires login.
def test_update_contribution_requires_login(monkeypatch, client):
    app.dependency_overrides.pop(get_auth_session, None)
    update = MagicMock()
    monkeypatch.setattr(
        participant_router.participant_service,
        "update_contribution",
        update,
    )
    response = client.patch(
        "/api/cart/1/participants/me",
        json={"amountcontributed": "20.00"},
    )
    assert response.status_code == 401
    update.assert_not_called()


# Checks that leaving reaches the service and returns no response body.
def test_leave_cart_route(
    monkeypatch, authenticated_client, user_session
):
    leave = MagicMock(return_value=None)
    monkeypatch.setattr(
        participant_router.participant_service,
        "leave_cart",
        leave,
    )
    response = authenticated_client.delete(
        "/api/cart/1/participants/me"
    )
    assert response.status_code == 204
    assert response.content == b""
    leave.assert_called_once_with(
        cart_id=1,
        session=user_session,
    )


# Checks that invalid cart IDs are rejected before calling the service.
@pytest.mark.parametrize("cart_id", ["0", "-1", "abc"])
def test_leave_cart_rejects_invalid_id(
    monkeypatch, authenticated_client, cart_id
):
    leave = MagicMock()
    monkeypatch.setattr(
        participant_router.participant_service,
        "leave_cart",
        leave,
    )
    response = authenticated_client.delete(
        f"/api/cart/{cart_id}/participants/me"
    )
    assert response.status_code == 422
    leave.assert_not_called()
