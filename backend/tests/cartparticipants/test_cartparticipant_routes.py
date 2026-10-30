from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.dependencies.auth import get_auth_session
from app.main import app
import app.routers.cartparticipant as participant_router


@pytest.fixture
def mock_service(monkeypatch):
    """Replace the service so route tests do not reach the database."""
    service = MagicMock()
    monkeypatch.setattr(participant_router, "participant_service", service)
    return service


# Checks that viewing participants returns the service's data.
def test_get_participants_route(
    authenticated_client, user_session, participant_row, mock_service
):
    mock_service.get_active_participants.return_value = [participant_row]
    response = authenticated_client.get("/api/cart/1/participants")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["userid"] == participant_row["userid"]
    mock_service.get_active_participants.assert_called_once_with(
        cart_id=1, session=user_session
    )


# Checks that viewing participants requires login.
def test_get_participants_requires_login(client, mock_service):
    app.dependency_overrides.pop(get_auth_session, None)
    response = client.get("/api/cart/1/participants")
    assert response.status_code == 401
    mock_service.get_active_participants.assert_not_called()


# Checks that a valid join reaches the service with the right user and amount.
def test_join_cart_route(
    authenticated_client, user_session, participant_row, mock_service
):
    mock_service.join_cart.return_value = participant_row
    response = authenticated_client.post(
        "/api/cart/1/participants", json={"amountcontributed": "10.50"}
    )
    assert response.status_code == 201
    assert response.json()["userid"] == user_session.user_id
    mock_service.join_cart.assert_called_once()
    arguments = mock_service.join_cart.call_args.kwargs
    assert arguments["cart_id"] == 1
    assert arguments["session"] is user_session
    assert str(arguments["body"].amountcontributed) == "10.50"


# Checks that invalid amounts and caller-supplied user IDs are rejected.
@pytest.mark.parametrize("body", [
    {"amountcontributed": "-1.00"},
    {"amountcontributed": "10.555"},
    {"amountcontributed": "10.00", "userid": 99},
])
def test_join_cart_rejects_invalid_body(authenticated_client, mock_service, body):
    response = authenticated_client.post("/api/cart/1/participants", json=body)
    assert response.status_code == 422
    mock_service.join_cart.assert_not_called()


# Checks that a valid contribution update reaches the service.
def test_update_contribution_route(
    authenticated_client, user_session, participant_row, mock_service
):
    mock_service.update_contribution.return_value = {
        **participant_row, "amountcontributed": "20.00"
    }
    response = authenticated_client.patch(
        "/api/cart/1/participants/me", json={"amountcontributed": "20.00"}
    )
    assert response.status_code == 200
    assert response.json()["userid"] == user_session.user_id
    mock_service.update_contribution.assert_called_once()
    arguments = mock_service.update_contribution.call_args.kwargs
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
    authenticated_client, mock_service, body
):
    response = authenticated_client.patch("/api/cart/1/participants/me", json=body)
    assert response.status_code == 422
    mock_service.update_contribution.assert_not_called()


# Checks that an expired-cart conflict reaches the caller.
def test_update_contribution_returns_conflict(authenticated_client, mock_service):
    mock_service.update_contribution.side_effect = HTTPException(409, "Cart has expired")
    response = authenticated_client.patch(
        "/api/cart/1/participants/me", json={"amountcontributed": "20.00"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Cart has expired"


# Checks that updating a contribution requires login.
def test_update_contribution_requires_login(client, mock_service):
    app.dependency_overrides.pop(get_auth_session, None)
    response = client.patch(
        "/api/cart/1/participants/me", json={"amountcontributed": "20.00"}
    )
    assert response.status_code == 401
    mock_service.update_contribution.assert_not_called()


# Checks that leaving reaches the service and returns an empty response.
def test_leave_cart_route(authenticated_client, user_session, mock_service):
    mock_service.leave_cart.return_value = None
    response = authenticated_client.delete("/api/cart/1/participants/me")
    assert response.status_code == 204
    assert response.content == b""
    mock_service.leave_cart.assert_called_once_with(cart_id=1, session=user_session)


# Checks that invalid cart IDs are rejected before reaching the service.
@pytest.mark.parametrize("cart_id", ["0", "-1", "abc"])
@pytest.mark.parametrize("method, path, service_method", [
    ("GET", "/api/cart/{cart_id}/participants", "get_active_participants"),
    ("DELETE", "/api/cart/{cart_id}/participants/me", "leave_cart"),
])
def test_participant_routes_reject_invalid_id(
    authenticated_client, mock_service, cart_id, method, path, service_method
):
    response = authenticated_client.request(method, path.format(cart_id=cart_id))
    assert response.status_code == 422
    getattr(mock_service, service_method).assert_not_called()
