import pytest
from fastapi import HTTPException

import app.repositories.cart as cart_repository


# Checks that the repository returns None when no cart is found.
def test_find_cart_returns_none_when_missing(fake_db):
    fake_db.table.return_value.execute.return_value.data = []

    result = cart_repository.find_cart(fake_db, cart_id=999)

    assert result is None