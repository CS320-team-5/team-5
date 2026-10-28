from datetime import datetime, timezone
from types import SimpleNamespace

import app.routers.cart as cart_module

FIXED_NOW = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)


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