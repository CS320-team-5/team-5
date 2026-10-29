import app.repositories.cartparticipant as repository
from decimal import Decimal

# Checks that an existing participant record is returned.
def test_find_participant_returns_record(fake_db):
    row = {"cartid": 1, "userid": 2, "status": "Active"}
    query = fake_db.table.return_value
    query.execute.return_value.data = [row]
    result = repository.find_participant(fake_db, 1, 2)
    assert result == row
    fake_db.table.assert_called_once_with("cartparticipant")
    query.eq.assert_any_call("cartid", 1)
    query.eq.assert_any_call("userid", 2)
    query.limit.assert_called_once_with(1)


# Checks that a user who never joined returns None.
def test_find_participant_returns_none_when_missing(fake_db):
    fake_db.table.return_value.execute.return_value.data = []
    result = repository.find_participant(fake_db, 1, 2)
    assert result is None


# Checks that previously inactive participation can still be found.
def test_find_participant_includes_inactive_records(fake_db):
    row = {"cartid": 1, "userid": 2, "status": "Inactive"}
    query = fake_db.table.return_value
    query.execute.return_value.data = [row]
    result = repository.find_participant(fake_db, 1, 2)
    assert result == row
    assert [call.args for call in query.eq.call_args_list] == [
        ("cartid", 1),
        ("userid", 2),
    ]


# Checks that the list query requests active users in the correct cart.
def test_get_active_participants_applies_filters(fake_db):
    rows = [{"cartid": 1, "userid": 2, "status": "Active"}]
    query = fake_db.table.return_value
    query.execute.return_value.data = rows
    result = repository.get_active_participants(fake_db, 1)
    assert result == rows
    fake_db.table.assert_called_once_with("cartparticipant")
    assert [call.args for call in query.eq.call_args_list] == [
        ("cartid", 1),
        ("status", "Active"),
    ]
    query.order.assert_called_once_with("userid")


# Checks that a cart with no active participants returns an empty list.
def test_get_active_participants_returns_empty_list(fake_db):
    fake_db.table.return_value.execute.return_value.data = []
    assert repository.get_active_participants(fake_db, 1) == []

# Checks that the update calls the database function with the right values.
def test_update_contribution_calls_database_function(fake_db):
    row = {
        "cartid": 1,
        "userid": 2,
        "status": "Active",
        "amountcontributed": "20.00",
        "joindate": "2026-10-28",
    }
    fake_db.rpc.return_value.execute.return_value.data = [row]
    result = repository.update_contribution(
        db=fake_db,
        cart_id=1,
        amount=Decimal("20.00"),
    )
    assert result == row
    fake_db.rpc.assert_called_once_with(
        "update_cart_contribution",
        {
            "p_cartid": 1,
            "p_amountcontributed": "20.00",
        },
    )
    fake_db.rpc.return_value.execute.assert_called_once_with()


# Checks that leaving calls the database function with the cart ID.
def test_leave_cart_calls_database_function(fake_db):
    row = {
        "cartid": 1,
        "userid": 2,
        "status": "Inactive",
        "amountcontributed": "20.00",
        "joindate": "2026-10-28",
    }
    fake_db.rpc.return_value.execute.return_value.data = [row]
    result = repository.leave_cart(
        db=fake_db,
        cart_id=1,
    )
    assert result == row
    fake_db.rpc.assert_called_once_with(
        "leave_cart",
        {"p_cartid": 1},
    )
    fake_db.rpc.return_value.execute.assert_called_once_with()


# Checks that no returned participant produces None.
def test_leave_cart_returns_none_when_empty(fake_db):
    fake_db.rpc.return_value.execute.return_value.data = []
    result = repository.leave_cart(
        db=fake_db,
        cart_id=1,
    )
    assert result is None