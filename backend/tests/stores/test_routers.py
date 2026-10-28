from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.auth import get_auth_session
from app.database import get_supabase
from app.routers import store as store_router


ROW = {"storeid": 1, "enterprisename": "Corner Market", "storetype": "Grocery",
       "address": "123 Main Street", "minimumorderamount": "10.50"}
BODY = {key: value for key, value in ROW.items() if key != "storeid"}


@pytest.fixture
def setup(monkeypatch):
    app = FastAPI()
    app.include_router(store_router.router)
    db = object()
    app.dependency_overrides[get_supabase] = lambda: db
    app.dependency_overrides[get_auth_session] = lambda: SimpleNamespace(db=db)
    mock_service = MagicMock()
    monkeypatch.setattr(store_router, "service", mock_service)
    with TestClient(app) as client:
        yield client, mock_service, db
    app.dependency_overrides.clear()


def test_post_returns_201(setup):
    client, service, db = setup
    service.create_store.return_value = ROW
    response = client.post("/api/store", json=BODY)
    assert response.status_code == 201
    assert response.json()["storeid"] == 1
    assert service.create_store.call_args.args[0] is db


@pytest.mark.parametrize("body", [
    {**BODY, "enterprisename": ""},
    {**BODY, "minimumorderamount": -1},
    {k: v for k, v in BODY.items() if k != "address"},
    {**BODY, "unexpected": True},
])
def test_post_bad_payload_returns_422(setup, body):
    client, service, _ = setup
    assert client.post("/api/store", json=body).status_code == 422
    service.create_store.assert_not_called()


def test_get_one_returns_200(setup):
    client, service, db = setup
    service.get_store.return_value = ROW
    response = client.get("/api/store/1")
    assert response.status_code == 200
    assert response.json()["storeid"] == 1
    service.get_store.assert_called_once_with(db, 1)


def test_get_one_missing_returns_404(setup):
    client, service, _ = setup
    service.get_store.side_effect = HTTPException(404, "missing")
    assert client.get("/api/store/9").status_code == 404


def test_get_all_returns_list(setup):
    client, service, db = setup
    service.get_all_stores.return_value = [ROW]
    response = client.get("/api/store")
    assert response.status_code == 200
    assert len(response.json()) == 1
    service.get_all_stores.assert_called_once_with(db, None)


def test_get_all_forwards_filter(setup):
    client, service, db = setup
    service.get_all_stores.return_value = []
    assert client.get("/api/store?storetype=Grocery").status_code == 200
    service.get_all_stores.assert_called_once_with(db, "Grocery")


@pytest.mark.parametrize("path", ["/api/store/0", "/api/store/-1", "/api/store/abc"])
def test_invalid_path_id_returns_422(setup, path):
    client, _, _ = setup
    assert client.get(path).status_code == 422


def test_patch_updates_store(setup):
    client, service, db = setup
    service.update_store.return_value = {**ROW, "address": "456 Oak Road"}
    response = client.patch("/api/store/1", json={"address": "456 Oak Road"})
    assert response.status_code == 200
    assert response.json()["address"] == "456 Oak Road"
    assert service.update_store.call_args.args[:2] == (db, 1)


def test_patch_bad_payload_returns_422(setup):
    client, service, _ = setup
    assert client.patch("/api/store/1", json={"minimumorderamount": -1}).status_code == 422
    service.update_store.assert_not_called()


def test_delete_returns_204_without_body(setup):
    client, service, db = setup
    response = client.delete("/api/store/1")
    assert response.status_code == 204
    assert response.content == b""
    service.delete_store.assert_called_once_with(db, 1)


def test_delete_missing_returns_404(setup):
    client, service, _ = setup
    service.delete_store.side_effect = HTTPException(404, "missing")
    assert client.delete("/api/store/9").status_code == 404
