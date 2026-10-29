from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.cartparticipant import ParticipantJoin, ParticipantUpdate
import app.services.cartparticipant as participant_service


@pytest.fixture
def mock_repository(monkeypatch):
    """Replace participant database calls for one service test."""
    repository = MagicMock()
    monkeypatch.setattr(participant_service, "participant_repository", repository)
    return repository


@pytest.fixture
def visible_cart(monkeypatch):
    """Pretend the cart exists and is visible to the user."""
    lookup = MagicMock(return_value={"cartid": 1})
    monkeypatch.setattr(participant_service.cart_service, "get_cart", lookup)
    return lookup


# Checks that participant records become response models.
def test_get_participants_returns_models(
    visible_cart, user_session, participant_row, mock_repository
):
    mock_repository.get_active_participants.return_value = [
        {**participant_row, "userid": 2}
    ]
    result = participant_service.get_active_participants(1, user_session)
    assert len(result) == 1
    assert result[0].userid == 2
    assert str(result[0].amountcontributed) == "10.50"
    visible_cart.assert_called_once_with(db=user_session.db, cart_id=1)
    mock_repository.get_active_participants.assert_called_once_with(user_session.db, 1)


# Checks that no active participants produces an empty list.
def test_get_participants_returns_empty_list(visible_cart, user_session, mock_repository):
    mock_repository.get_active_participants.return_value = []
    assert participant_service.get_active_participants(1, user_session) == []


# Checks that a missing cart stops the participant lookup.
def test_missing_cart_prevents_participant_lookup(
    visible_cart, user_session, mock_repository
):
    visible_cart.side_effect = HTTPException(404, "Cart not found")
    with pytest.raises(HTTPException) as error:
        participant_service.get_active_participants(1, user_session)
    assert error.value.status_code == 404
    mock_repository.get_active_participants.assert_not_called()


# Checks that joining uses the signed-in user's connection and amount.
def test_join_cart_returns_participant(user_session, participant_row, mock_repository):
    mock_repository.join_cart.return_value = participant_row
    body = ParticipantJoin(amountcontributed="10.50")
    result = participant_service.join_cart(1, body, user_session)
    assert result.userid == user_session.user_id
    assert result.amountcontributed == body.amountcontributed
    mock_repository.join_cart.assert_called_once_with(
        db=user_session.db, cart_id=1, amount=body.amountcontributed
    )


# Checks that no returned participant produces a join error.
def test_join_cart_without_result_returns_502(user_session, mock_repository):
    mock_repository.join_cart.return_value = None
    with pytest.raises(HTTPException) as error:
        participant_service.join_cart(1, ParticipantJoin(amountcontributed="10.50"), user_session)
    assert error.value.status_code == 502


# Checks that updating sends the new amount using the user's connection.
def test_update_contribution_returns_participant(
    user_session, participant_row, mock_repository
):
    mock_repository.update_contribution.return_value = {
        **participant_row, "amountcontributed": "20.00"
    }
    body = ParticipantUpdate(amountcontributed="20.00")
    result = participant_service.update_contribution(1, body, user_session)
    assert result.userid == user_session.user_id
    assert result.amountcontributed == body.amountcontributed
    mock_repository.update_contribution.assert_called_once_with(
        db=user_session.db, cart_id=1, amount=body.amountcontributed
    )


# Checks that no returned participant produces an update error.
def test_update_contribution_without_result_returns_502(user_session, mock_repository):
    mock_repository.update_contribution.return_value = None
    with pytest.raises(HTTPException) as error:
        participant_service.update_contribution(
            1, ParticipantUpdate(amountcontributed="20.00"), user_session
        )
    assert error.value.status_code == 502


# Checks that leaving uses the signed-in user's connection.
def test_leave_cart_succeeds(user_session, mock_repository):
    mock_repository.leave_cart.return_value = {
        "cartid": 1, "userid": user_session.user_id, "status": "Inactive"
    }
    assert participant_service.leave_cart(1, user_session) is None
    mock_repository.leave_cart.assert_called_once_with(db=user_session.db, cart_id=1)


# Checks that no returned participant produces a leave error.
def test_leave_cart_without_result_returns_502(user_session, mock_repository):
    mock_repository.leave_cart.return_value = None
    with pytest.raises(HTTPException) as error:
        participant_service.leave_cart(1, user_session)
    assert error.value.status_code == 502
