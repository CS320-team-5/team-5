from unittest.mock import MagicMock
import pytest
from app.repositories import statistics_repository as repo


@pytest.fixture
def fake_db(monkeypatch):
    client = MagicMock()
    response = MagicMock()
    response.data = [{"test": True}]
    client.table.return_value.select.return_value.execute.return_value = response
    client.table.return_value.select.return_value.eq.return_value.execute.return_value = response
    client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = response
    monkeypatch.setattr(repo, "sb", client)
    return client, response


@pytest.mark.parametrize("function,table", [
    ("get_users_table", "users"),
    ("get_carts_table", "cart"),
    ("get_stores_table", "store"),
    ("get_cart_participants_table", "cartparticipant"),
    ("get_review_table", "review"),
])
def test_fetch_entire_table(fake_db, function, table):
    client, response = fake_db
    assert getattr(repo, function)() is response
    client.table.assert_called_once_with(table)
    client.table.return_value.select.assert_called_once_with("*")


@pytest.mark.parametrize("function,kwargs,column,value", [
    ("get_users_table", {"user_id": 5}, "userid", 5),
    ("get_carts_table", {"cart_id": 7}, "cartid", 7),
    ("get_stores_table", {"store_id": 3}, "storeid", 3),
    ("get_stores_table", {"enterprise_name": "Example"}, "enterprisename", "Example"),
    ("get_cart_participants_table", {"user_id": 5}, "userid", 5),
    ("get_cart_participants_table", {"cart_id": 7}, "cartid", 7),
    ("get_review_table", {"target_user_id": 5}, "targetuserid", 5),
])
def test_repository_filters(fake_db, function, kwargs, column, value):
    client, response = fake_db
    assert getattr(repo, function)(**kwargs) is response
    client.table.return_value.select.return_value.eq.assert_called_with(column, value)


def test_cart_participant_filters_by_both_keys(fake_db):
    client, _ = fake_db
    repo.get_cart_participants_table(cart_id=7, user_id=5)
    eq = client.table.return_value.select.return_value.eq
    eq.assert_any_call("cartid", 7)
    eq.return_value.eq.assert_called_once_with("userid", 5)
