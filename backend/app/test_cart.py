from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from app.cart import check_owner
from pydantic import ValidationError
from app.cart import CartCreate, CartUpdate
from unittest.mock import MagicMock

import httpx
from postgrest.exceptions import APIError

import app.cart as cart_module
# Checks that the owner passes the ownership check.
def test_owner_can_edit_cart():
    cart = SimpleNamespace(owneruserid=1)
    check_owner(cart, user_id=1)

# Checks that someone other than the owner is rejected.
def test_other_user_cannot_edit_cart():
    cart = SimpleNamespace(owneruserid=1)
    with pytest.raises(HTTPException) as error:
        check_owner(cart, user_id=2)
    assert error.value.status_code == 403

# Checks that a cart cannot have a negative minimum amount.
def test_create_cart_rejects_negative_amount():
    with pytest.raises(ValidationError):
        CartCreate(
            storeid=1,
            location="Amherst",
            deadline="2026-12-01T18:00:00-05:00",
            minimumamount="-1.00",
        )

# Checks that a store ID of zero is rejected.
def test_create_cart_rejects_invalid_store_id():
    with pytest.raises(ValidationError):
        CartCreate(
            storeid=0,
            location="Amherst",
            deadline="2026-12-01T18:00:00-05:00",
            minimumamount="25.00",
        )

# Checks that locations longer than 30 characters are rejected.
def test_create_cart_rejects_long_location():
    with pytest.raises(ValidationError):
        CartCreate(
            storeid=1,
            location="A" * 31,
            deadline="2026-12-01T18:00:00-05:00",
            minimumamount="25.00",
        )

# Checks that an unknown cart status is rejected.
def test_update_cart_rejects_invalid_status():
    with pytest.raises(ValidationError):
        CartUpdate(status="Unknown")

# Checks that the minimum amount cannot be zero.
def test_create_cart_rejects_zero_minimum():
    with pytest.raises(ValidationError):
        CartCreate(
            storeid=1,
            location="Amherst",
            deadline="2026-12-01T18:00:00-05:00",
            minimumamount="0.00",
        )

# Checks that a deadline must be provided when creating a cart.
def test_create_cart_requires_deadline():
    with pytest.raises(ValidationError):
        CartCreate(
            storeid=1,
            location="Amherst",
            minimumamount="25.00",
        )

# Checks that a deadline must include a time zone.
def test_create_cart_rejects_deadline_without_timezone():
    with pytest.raises(ValidationError):
        CartCreate(
            storeid=1,
            location="Amherst",
            deadline="2026-12-01T18:00:00",
            minimumamount="25.00",
        )

#ADD MOCK DB FOR TESTS
@pytest.fixture
def cart_row():
    return {
        "cartid": 1,
        "storeid": 1,
        "owneruserid": 1,
        "location": "Amherst",
        "deadline": "2026-12-01T18:00:00-05:00",
        "minimumamount": "25.00",
        "currentamount": "0.00",
        "status": "Active",
    }

@pytest.fixture
def fake_db():
    db = MagicMock()
    query = db.table.return_value
    # Allow the chained calls used by cart.py.
    for method in (
        "select", "insert", "update", "delete",
        "eq", "neq", "gt", "lte", "limit", "order",
    ):
        getattr(query, method).return_value = query
    return db

@pytest.fixture
def session(fake_db):
    return SimpleNamespace(db=fake_db, user_id=1)

# Checks that valid cart details are accepted.
def test_create_cart_accepts_valid_data():
    cart = CartCreate(
        storeid=1,
        location="Amherst",
        deadline="2026-12-01T18:00:00-05:00",
        minimumamount="25.00",
    )
    assert cart.storeid == 1
    assert cart.minimumamount == 25
    assert cart.deadline.utcoffset() is not None

# Checks that an updated minimum amount must be greater than zero.
@pytest.mark.parametrize("amount", ["-1.00", "0.00"])
def test_update_cart_rejects_nonpositive_minimum(amount):
    with pytest.raises(ValidationError):
        CartUpdate(minimumamount=amount)

# Checks that a missing cart returns a not-found error.
def test_find_cart_returns_404_when_missing(fake_db):
    fake_db.table.return_value.execute.return_value.data = []
    with pytest.raises(HTTPException) as error:
        cart_module.find_cart(fake_db, cart_id=999)
    assert error.value.status_code == 404

# Checks that the signed-in user becomes the cart owner and no cart ID is supplied.
def test_create_cart_uses_session_owner(cart_row, session):
    row = {**cart_row, "owneruserid": 7}
    session.user_id = 7
    query = session.db.table.return_value
    query.execute.return_value.data = [row]
    result = cart_module.create_cart(
        body=CartCreate(
            storeid=1,
            location="Amherst",
            deadline="2026-12-01T18:00:00-05:00",
            minimumamount="25.00",
        ),
        session=session,
    )
    values = query.insert.call_args.args[0]
    assert values["owneruserid"] == 7
    assert "cartid" not in values
    assert result.owneruserid == 7

# Checks that another user cannot update or delete the cart, and no database call is made.
@pytest.mark.parametrize("action", ["update", "delete"])
def test_nonowner_cannot_change_cart(
    monkeypatch, cart_row, session, action
):
    cart = cart_module.Cart(**{
        **cart_row,
        "owneruserid": 2,
    })
    monkeypatch.setattr(
        cart_module, "find_cart", lambda db, cart_id: cart
    )
    with pytest.raises(HTTPException) as error:
        if action == "update":
            cart_module.update_cart(
                body=CartUpdate(location="Boston"),
                cart_id=1,
                session=session,
            )
        else:
            cart_module.delete_cart(
                cart_id=1,
                session=session,
            )
    assert error.value.status_code == 403
    session.db.table.assert_not_called()

# Freeze only cart.py's clock. No network or real database is used.
from datetime import datetime, timedelta, timezone


FIXED_NOW = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)

@pytest.fixture(autouse=True)
def fixed_cart_clock(monkeypatch):
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            if tz is None:
                return FIXED_NOW.replace(tzinfo=None)
            return FIXED_NOW.astimezone(tz)

    monkeypatch.setattr(cart_module, "datetime", FixedDatetime)

@pytest.fixture
def future_cart(cart_row):
    return cart_module.Cart(**{
        **cart_row,
        "deadline": (FIXED_NOW + timedelta(days=2)).isoformat(),
    })

@pytest.fixture
def full_cart(monkeypatch, future_cart):
    monkeypatch.setattr(
        cart_module, "find_cart", lambda db, cart_id: future_cart
    )
    return future_cart

# Checks that a past deadline is rejected before anything is saved.
def test_create_past_deadline_does_not_insert(session):
    body = CartCreate(
        storeid=1,
        deadline=FIXED_NOW - timedelta(seconds=1),
        minimumamount="25.00",
    )
    with pytest.raises(HTTPException) as error:
        cart_module.create_cart(body=body, session=session)
    assert error.value.status_code == 422
    session.db.table.assert_not_called()

# Checks that a deadline set to the current time is rejected before saving.
def test_create_deadline_equal_to_now_does_not_insert(session):
    body = CartCreate(storeid=1, deadline=FIXED_NOW, minimumamount="25.00")
    with pytest.raises(HTTPException) as error:
        cart_module.create_cart(body=body, session=session)
    assert error.value.status_code == 422
    session.db.table.assert_not_called()

# Checks that the history query asks for this owner's past carts, newest first.
def test_history_requests_owner_past_carts_newest_first(session, cart_row):
    row = {**cart_row, "deadline": (FIXED_NOW - timedelta(days=1)).isoformat()}
    query = session.db.table.return_value
    query.execute.return_value.data = [row]
    result = cart_module.get_cart_history(session=session)
    session.db.table.assert_called_once_with("cart")
    query.eq.assert_called_once_with("owneruserid", session.user_id)
    query.lte.assert_called_once_with("deadline", FIXED_NOW.isoformat())
    query.order.assert_called_once_with("deadline", desc=True)
    assert [cart.cartid for cart in result] == [row["cartid"]]

# Checks that no past carts produces an empty history list.
def test_history_without_rows_returns_empty_list(session):
    session.db.table.return_value.execute.return_value.data = []
    assert cart_module.get_cart_history(session=session) == []


# Checks that a cart cannot be edited at or after its deadline.
@pytest.mark.parametrize("seconds_ago", [0, 1])
def test_expired_cart_cannot_be_edited(monkeypatch, future_cart, session, seconds_ago):
    expired = future_cart.model_copy(update={
        "deadline": FIXED_NOW - timedelta(seconds=seconds_ago)
    })
    monkeypatch.setattr(cart_module, "find_cart", lambda db, cart_id: expired)
    with pytest.raises(HTTPException) as error:
        cart_module.update_cart(
            body=CartUpdate(location="Boston"), cart_id=1, session=session
        )
    assert error.value.status_code == 409
    session.db.table.assert_not_called()


# Checks that the owner cannot move a deadline into the past.
def test_new_deadline_cannot_be_in_past(full_cart, session):
    with pytest.raises(HTTPException) as error:
        cart_module.update_cart(
            body=CartUpdate(deadline=FIXED_NOW - timedelta(seconds=1)),
            cart_id=1, session=session,
        )
    assert error.value.status_code == 422
    session.db.table.assert_not_called()

# Checks that an owner with no other active participants can change details or close early.
@pytest.mark.parametrize("changes", [
    {"location": "Boston"},
    {"minimumamount": "30.00"},
    {"deadline": FIXED_NOW + timedelta(hours=1)},
    {"status": "Inactive"},
    {"location": None},
])
def test_owner_alone_can_change_cart(full_cart, session, changes):
    body = CartUpdate(**changes)
    updated = full_cart.model_copy(update=body.model_dump(exclude_unset=True))
    query = session.db.table.return_value
    query.execute.side_effect = [
        SimpleNamespace(data=[]),  # No other active participants.
        SimpleNamespace(data=[updated.model_dump(mode="json")]),
    ]
    result = cart_module.update_cart(body=body, cart_id=1, session=session)
    assert result == updated
    query.update.assert_called_once_with(body.model_dump(mode="json", exclude_unset=True))
    query.eq.assert_any_call("owneruserid", session.user_id)

# Checks that joining users prevent early closing, a shorter deadline, and location or minimum changes.
@pytest.mark.parametrize("changes", [
    {"status": "Inactive"},
    {"deadline": FIXED_NOW + timedelta(hours=1)},
    {"location": "Boston"},
    {"minimumamount": "30.00"},
])

def test_participants_prevent_unwanted_updates(
    full_cart, session, changes
):
    query = session.db.table.return_value
    query.execute.return_value.data = [{"userid": 2}]

    with pytest.raises(HTTPException) as error:
        cart_module.update_cart(
            body=CartUpdate(**changes),
            cart_id=1,
            session=session,
        )

    assert error.value.status_code == 409
    query.update.assert_not_called()

# Checks that the owner can extend the deadline even after another user joins.
def test_participants_allow_deadline_extension(full_cart, session):
    deadline = full_cart.deadline + timedelta(days=1)
    updated = full_cart.model_copy(update={"deadline": deadline})

    query = session.db.table.return_value
    query.execute.side_effect = [
        SimpleNamespace(data=[{"userid": 2}]),
        SimpleNamespace(data=[updated.model_dump(mode="json")]),
    ]

    result = cart_module.update_cart(
        body=CartUpdate(deadline=deadline),
        cart_id=1,
        session=session,
    )

    assert result.deadline == deadline
    query.update.assert_called_once()


# Checks that ended carts cannot be deleted, preserving their history.
@pytest.mark.parametrize("seconds_ago", [0, 1])
def test_delete_rejects_ended_cart(
    monkeypatch, future_cart, session, seconds_ago
):
    expired = future_cart.model_copy(update={
        "deadline": FIXED_NOW - timedelta(seconds=seconds_ago),
    })

    monkeypatch.setattr(
        cart_module, "find_cart", lambda db, cart_id: expired
    )

    with pytest.raises(HTTPException) as error:
        cart_module.delete_cart(cart_id=1, session=session)

    assert error.value.status_code == 409
    session.db.table.assert_not_called()

# Checks that a future cart with no other participant records can be deleted.
def test_delete_future_cart_without_others(full_cart, session):
    query = session.db.table.return_value
    query.execute.side_effect = [
        SimpleNamespace(data=[]),
        SimpleNamespace(data=[full_cart.model_dump(mode="json")]),
    ]
    response = cart_module.delete_cart(
        cart_id=1,
        session=session,
    )
    assert response.status_code == 204
    assert response.body == b""
    query.delete.assert_called_once()
    query.eq.assert_any_call("cartid", full_cart.cartid)
    query.eq.assert_any_call("owneruserid", session.user_id)
    query.gt.assert_called_once_with(
        "deadline", FIXED_NOW.isoformat()
    )