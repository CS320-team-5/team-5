from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.models.cart import Cart
import app.services.cart as cart_service

FIXED_NOW = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)


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
def session(fake_db):
    return SimpleNamespace(db=fake_db, user_id=1)

@pytest.fixture(autouse=True)
def fixed_cart_clock(monkeypatch):
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            if tz is None:
                return FIXED_NOW.replace(tzinfo=None)
            return FIXED_NOW.astimezone(tz)

    monkeypatch.setattr(cart_service, "datetime", FixedDatetime)

@pytest.fixture
def future_cart(cart_row):
    return Cart(**{
        **cart_row,
        "deadline": (FIXED_NOW + timedelta(days=2)).isoformat(),
    })

@pytest.fixture
def full_cart(monkeypatch, future_cart):

    monkeypatch.setattr(
        cart_service, "find_cart", lambda db, cart_id: future_cart
    )
    return future_cart
