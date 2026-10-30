from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.store import Store, StoreCreate, StoreUpdate
from app.services import store_service as service


ROW = {"storeid": 1, "enterprisename": "Corner Market", "storetype": "Grocery",
       "address": "123 Main Street", "minimumorderamount": "10.50"}


@pytest.fixture
def repo(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(service, "repository", fake)
    return fake


@pytest.fixture
def db():
    return object()


def test_create_returns_store(db, repo):
    repo.create_store_record.return_value = [ROW]
    body = StoreCreate(**{k: v for k, v in ROW.items() if k != "storeid"})
    result = service.create_store(db, body)
    assert isinstance(result, Store)
    assert result.storeid == 1
    repo.create_store_record.assert_called_once_with(db, body.model_dump(mode="json"))


def test_create_no_result_raises_502(db, repo):
    repo.create_store_record.return_value = []
    body = StoreCreate(**{k: v for k, v in ROW.items() if k != "storeid"})
    with pytest.raises(HTTPException) as error:
        service.create_store(db, body)
    assert error.value.status_code == 502


def test_get_returns_repository_result(db, repo):
    expected = Store(**ROW)
    repo.find_store.return_value = expected
    assert service.get_store(db, 1) is expected
    repo.find_store.assert_called_once_with(db, 1)


def test_get_propagates_not_found(db, repo):
    repo.find_store.side_effect = HTTPException(404, "missing")
    with pytest.raises(HTTPException) as error:
        service.get_store(db, 4)
    assert error.value.status_code == 404


def test_get_all_converts_rows_to_models(db, repo):
    repo.get_all_store_records.return_value = [ROW, {**ROW, "storeid": 2}]
    stores = service.get_all_stores(db, "Grocery")
    assert [store.storeid for store in stores] == [1, 2]
    repo.get_all_store_records.assert_called_once_with(db, "Grocery")


def test_get_all_empty(db, repo):
    repo.get_all_store_records.return_value = []
    assert service.get_all_stores(db) == []


def test_update_changes_one_field(db, repo):
    repo.find_store.return_value = Store(**ROW)
    repo.update_store_record.return_value = [{**ROW, "address": "456 Oak Road"}]
    result = service.update_store(db, 1, StoreUpdate(address="456 Oak Road"))
    assert result.address == "456 Oak Road"
    repo.update_store_record.assert_called_once_with(db, 1, {"address": "456 Oak Road"})


def test_update_empty_payload_skips_write(db, repo):
    existing = Store(**ROW)
    repo.find_store.return_value = existing
    assert service.update_store(db, 1, StoreUpdate()) is existing
    repo.update_store_record.assert_not_called()


def test_update_rejects_explicit_null(db, repo):
    repo.find_store.return_value = Store(**ROW)
    with pytest.raises(HTTPException) as error:
        service.update_store(db, 1, StoreUpdate(address=None))
    assert error.value.status_code == 422
    repo.update_store_record.assert_not_called()


def test_update_missing_store_propagates_404(db, repo):
    repo.find_store.side_effect = HTTPException(404)
    with pytest.raises(HTTPException) as error:
        service.update_store(db, 1, StoreUpdate(address="new"))
    assert error.value.status_code == 404
    repo.update_store_record.assert_not_called()


def test_update_no_row_raises_409(db, repo):
    repo.find_store.return_value = Store(**ROW)
    repo.update_store_record.return_value = []
    with pytest.raises(HTTPException) as error:
        service.update_store(db, 1, StoreUpdate(address="new"))
    assert error.value.status_code == 409


def test_delete_existing_store(db, repo):
    repo.find_store.return_value = Store(**ROW)
    repo.delete_store_record.return_value = [{"storeid": 1}]
    assert service.delete_store(db, 1) is None
    repo.delete_store_record.assert_called_once_with(db, 1)


def test_delete_missing_store_propagates_404(db, repo):
    repo.find_store.side_effect = HTTPException(404)
    with pytest.raises(HTTPException) as error:
        service.delete_store(db, 1)
    assert error.value.status_code == 404
    repo.delete_store_record.assert_not_called()


def test_delete_empty_result_raises_409(db, repo):
    repo.find_store.return_value = Store(**ROW)
    repo.delete_store_record.return_value = []
    with pytest.raises(HTTPException) as error:
        service.delete_store(db, 1)
    assert error.value.status_code == 409
