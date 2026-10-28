from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from httpx import RequestError
from postgrest.exceptions import APIError

from app.repositories import store_repository as repository
from app.models.store import Store


ROW = {"storeid": 1, "enterprisename": "Corner Market", "storetype": "Grocery",
       "address": "123 Main Street", "minimumorderamount": "10.50"}


@pytest.fixture
def db():
    database = MagicMock()
    # MagicMock returns the same chain object for each query method.
    query = database.table.return_value
    query.select.return_value = query
    query.eq.return_value = query
    query.limit.return_value = query
    query.order.return_value = query
    query.insert.return_value = query
    query.update.return_value = query
    query.delete.return_value = query
    query.execute.return_value.data = [ROW]
    return database


def test_find_store_returns_model(db):
    result = repository.find_store(db, 1)
    assert isinstance(result, Store)
    assert result.storeid == 1
    db.table.assert_called_with("store")
    db.table.return_value.eq.assert_called_with("storeid", 1)
    db.table.return_value.limit.assert_called_once_with(1)


def test_find_store_raises_404_for_no_rows(db):
    db.table.return_value.execute.return_value.data = []
    with pytest.raises(HTTPException) as error:
        repository.find_store(db, 1)
    assert error.value.status_code == 404


def test_create_store_builds_insert(db):
    assert repository.create_store_record(db, {"enterprisename": "Corner Market"}) == [ROW]
    db.table.return_value.insert.assert_called_once_with({"enterprisename": "Corner Market"})
    db.table.return_value.select.assert_called_once_with("*")


def test_list_stores_orders_by_id(db):
    assert repository.get_all_store_records(db) == [ROW]
    db.table.return_value.order.assert_called_once_with("storeid")
    db.table.return_value.eq.assert_not_called()


def test_list_stores_filters_type(db):
    repository.get_all_store_records(db, "Grocery")
    db.table.return_value.eq.assert_called_once_with("storetype", "Grocery")


def test_update_store_builds_update_query(db):
    changes = {"address": "456 Oak Road"}
    assert repository.update_store_record(db, 1, changes) == [ROW]
    db.table.return_value.update.assert_called_once_with(changes)
    db.table.return_value.eq.assert_called_once_with("storeid", 1)
    db.table.return_value.select.assert_called_once_with("*")


def test_delete_store_builds_delete_query(db):
    assert repository.delete_store_record(db, 1) == [ROW]
    db.table.return_value.delete.assert_called_once_with()
    db.table.return_value.eq.assert_called_once_with("storeid", 1)
    db.table.return_value.select.assert_called_once_with("storeid")


@pytest.mark.parametrize("code,status", [
    ("23503", 409), ("23505", 409), ("42501", 403),
    ("PGRST301", 403), ("PGRST302", 403),
    ("23502", 422), ("23514", 422), ("22003", 422),
    ("unexpected", 503),
])
def test_database_errors_translate_to_http_status(db, code, status):
    db.table.return_value.execute.side_effect = APIError({"code": code, "message": "failure"})
    with pytest.raises(HTTPException) as error:
        repository.get_all_store_records(db)
    assert error.value.status_code == status


def test_network_error_becomes_503(db):
    db.table.return_value.execute.side_effect = RequestError("network error")
    with pytest.raises(HTTPException) as error:
        repository.get_all_store_records(db)
    assert error.value.status_code == 503
