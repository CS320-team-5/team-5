from decimal import Decimal

import app.repositories.cartparticipant as repository


# Checks that an existing participant record is returned.
def test_find_participant_returns_record(fake_db, participant_row):
    row = {**participant_row, "userid": 2}
    query = fake_db.table.return_value
    query.execute.return_value.data = [row]
    assert repository.find_participant(fake_db, 1, 2) == row
    fake_db.table.assert_called_once_with("cartparticipant")
    query.eq.assert_any_call("cartid", 1)
    query.eq.assert_any_call("userid", 2)
    query.limit.assert_called_once_with(1)


# Checks that a user who never joined returns None.
def test_find_participant_returns_none_when_missing(fake_db):
    fake_db.table.return_value.execute.return_value.data = []
    assert repository.find_participant(fake_db, 1, 2) is None


# Checks that inactive participation can still be found, without a status filter.
def test_find_participant_includes_inactive_records(fake_db, participant_row):
    row = {**participant_row, "userid": 2, "status": "Inactive"}
    query = fake_db.table.return_value
    query.execute.return_value.data = [row]
    assert repository.find_participant(fake_db, 1, 2) == row
    assert [call.args for call in query.eq.call_args_list] == [
        ("cartid", 1), ("userid", 2)
    ]


# Checks that the list query requests active users in the correct cart.
def test_get_active_participants_applies_filters(fake_db, participant_row):
    rows = [{**participant_row, "userid": 2}]
    query = fake_db.table.return_value
    query.execute.return_value.data = rows
    assert repository.get_active_participants(fake_db, 1) == rows
    fake_db.table.assert_called_once_with("cartparticipant")
    assert [call.args for call in query.eq.call_args_list] == [
        ("cartid", 1), ("status", "Active")
    ]
    query.order.assert_called_once_with("userid")


# Checks that no active participants produces an empty list.
def test_get_active_participants_returns_empty_list(fake_db):
    fake_db.table.return_value.execute.return_value.data = []
    assert repository.get_active_participants(fake_db, 1) == []


# Checks the database function name, amount, and returned update record.
def test_update_contribution_calls_database_function(fake_db, participant_row):
    row = {**participant_row, "userid": 2, "amountcontributed": "20.00"}
    fake_db.rpc.return_value.execute.return_value.data = [row]
    assert repository.update_contribution(fake_db, 1, Decimal("20.00")) == row
    fake_db.rpc.assert_called_once_with(
        "update_cart_contribution", {"p_cartid": 1, "p_amountcontributed": "20.00"}
    )
    fake_db.rpc.return_value.execute.assert_called_once_with()


# Checks the database function name, cart ID, and returned leave record.
def test_leave_cart_calls_database_function(fake_db, participant_row):
    row = {
        **participant_row, "userid": 2,
        "status": "Inactive", "amountcontributed": "20.00",
    }
    fake_db.rpc.return_value.execute.return_value.data = [row]
    assert repository.leave_cart(fake_db, 1) == row
    fake_db.rpc.assert_called_once_with("leave_cart", {"p_cartid": 1})
    fake_db.rpc.return_value.execute.assert_called_once_with()


# Checks that no returned participant produces None.
def test_leave_cart_returns_none_when_empty(fake_db):
    fake_db.rpc.return_value.execute.return_value.data = []
    assert repository.leave_cart(fake_db, 1) is None
