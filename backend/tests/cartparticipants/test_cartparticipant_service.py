from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

import app.services.cartparticipant as participant_service
from app.models.cartparticipant import ParticipantJoin
from app.models.cartparticipant import ParticipantUpdate

@pytest.fixture
def visible_cart(monkeypatch):
    # Pretend the cart exists and the user can view it.
    lookup = MagicMock(return_value={"cartid": 1})

    monkeypatch.setattr(
        participant_service.cart_service,
        "get_cart",
        lookup,
    )

    return lookup

# Checks that participant records become response models.
def test_get_participants_returns_models(
    monkeypatch, visible_cart, user_session
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
        participant_service.participant_repository,
        "get_active_participants",
        lookup,
    )

    result = participant_service.get_active_participants(
        cart_id=1,
        session=user_session,
    )

    assert len(result) == 1
    assert result[0].userid == 2
    assert str(result[0].amountcontributed) == "10.50"

    visible_cart.assert_called_once_with(
        db=user_session.db,
        cart_id=1,
    )
    lookup.assert_called_once_with(user_session.db, 1)

# Checks that no active participants produces an empty list.
def test_get_participants_returns_empty_list(
    monkeypatch, visible_cart, user_session
):
    monkeypatch.setattr(
        participant_service.participant_repository,
        "get_active_participants",
        MagicMock(return_value=[]),
    )

    result = participant_service.get_active_participants(
        cart_id=1,
        session=user_session,
    )

    assert result == []


# Checks that a missing cart stops the participant lookup.
def test_missing_cart_prevents_participant_lookup(
    monkeypatch, visible_cart, user_session
):
    visible_cart.side_effect = HTTPException(404, "Cart not found")

    lookup = MagicMock()
    monkeypatch.setattr(
        participant_service.participant_repository,
        "get_active_participants",
        lookup,
    )

    with pytest.raises(HTTPException) as error:
        participant_service.get_active_participants(
            cart_id=1,
            session=user_session,
        )

    assert error.value.status_code == 404
    lookup.assert_not_called()

# Checks that joining uses the signed-in user's database connection.
def test_join_cart_returns_participant(monkeypatch, user_session):
    row = {
        "cartid": 1,
        "userid": user_session.user_id,
        "status": "Active",
        "amountcontributed": "10.50",
        "joindate": "2026-10-28",
    }

    join = MagicMock(return_value=row)
    monkeypatch.setattr(
        participant_service.participant_repository,
        "join_cart",
        join,
    )

    body = ParticipantJoin(amountcontributed="10.50")

    result = participant_service.join_cart(
        cart_id=1,
        body=body,
        session=user_session,
    )

    assert result.userid == user_session.user_id
    assert result.amountcontributed == body.amountcontributed

    join.assert_called_once_with(
        db=user_session.db,
        cart_id=1,
        amount=body.amountcontributed,
    )


# Checks that joining reports an error if no participant is returned.
def test_join_cart_without_result_returns_502(
    monkeypatch, user_session
):
    monkeypatch.setattr(
        participant_service.participant_repository,
        "join_cart",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as error:
        participant_service.join_cart(
            cart_id=1,
            body=ParticipantJoin(amountcontributed="10.50"),
            session=user_session,
        )

    assert error.value.status_code == 502

# Checks that the service sends the new amount using the user's connection.
def test_update_contribution_returns_participant(
    monkeypatch, user_session
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
        participant_service.participant_repository,
        "update_contribution",
        update,
    )

    body = ParticipantUpdate(amountcontributed="20.00")

    result = participant_service.update_contribution(
        cart_id=1,
        body=body,
        session=user_session,
    )

    assert result.userid == user_session.user_id
    assert result.amountcontributed == body.amountcontributed
    update.assert_called_once_with(
        db=user_session.db,
        cart_id=1,
        amount=body.amountcontributed,
    )


# Checks that an empty database result produces an error.
def test_update_contribution_without_result_returns_502(
    monkeypatch, user_session
):
    monkeypatch.setattr(
        participant_service.participant_repository,
        "update_contribution",
        MagicMock(return_value=None),
    )

    with pytest.raises(HTTPException) as error:
        participant_service.update_contribution(
            cart_id=1,
            body=ParticipantUpdate(amountcontributed="20.00"),
            session=user_session,
        )
    assert error.value.status_code == 502

# Checks that leaving uses the signed-in user's connection.
def test_leave_cart_succeeds(monkeypatch, user_session):
    leave = MagicMock(return_value={
        "cartid": 1,
        "userid": user_session.user_id,
        "status": "Inactive",
    })
    monkeypatch.setattr(
        participant_service.participant_repository,
        "leave_cart",
        leave,
    )
    result = participant_service.leave_cart(
        cart_id=1,
        session=user_session,
    )
    assert result is None
    leave.assert_called_once_with(
        db=user_session.db,
        cart_id=1,
    )


# Checks that an empty database result produces an error.
def test_leave_cart_without_result_returns_502(
    monkeypatch, user_session
):
    monkeypatch.setattr(
        participant_service.participant_repository,
        "leave_cart",
        MagicMock(return_value=None),
    )
    with pytest.raises(HTTPException) as error:
        participant_service.leave_cart(
            cart_id=1,
            session=user_session,
        )
    assert error.value.status_code == 502
