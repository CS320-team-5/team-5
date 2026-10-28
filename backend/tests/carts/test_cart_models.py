import pytest
from pydantic import ValidationError

from app.models.cart import CartCreate, CartUpdate

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
