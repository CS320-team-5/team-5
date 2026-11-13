from unittest.mock import Mock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers import statistics as statistics_router


@pytest.fixture
def client(monkeypatch):
    svc = statistics_router.statistics_service
    handlers = {
        "get_user_statistics": lambda uid: {"user_id": uid, "total_spending": 60.0,
                                             "average_contribution": 30.0, "average_rating": 4.0},
        "get_user_cart_statistics": lambda user_id, cart_id: {
            "user_id": user_id, "cart_id": cart_id, "total_contribution": 20.0},
        "get_store_statistics": lambda sid: {
            "store_id": sid, "total_open_carts": 2, "total_spending": 140.0},
        "get_enterprise_statistics": lambda name: {
            "enterprise_name": name, "total_locations": 3},
    }
    mocks = {}
    for name, action in handlers.items():
        mocked = Mock(side_effect=action)
        monkeypatch.setattr(svc, name, mocked)
        mocks[name] = mocked
    app = FastAPI()
    app.include_router(statistics_router.router)
    return TestClient(app), mocks


def test_user_endpoint(client):
    http, mocks = client
    r = http.get("/statistics/users/1")
    assert r.status_code == 200
    assert r.json()["average_rating"] == 4.0
    mocks["get_user_statistics"].assert_called_once_with(1)


def test_cart_endpoint(client):
    http, mocks = client
    r = http.get("/statistics/carts/10/users/1")
    assert r.status_code == 200
    assert r.json()["total_contribution"] == 20.0
    mocks["get_user_cart_statistics"].assert_called_once_with(user_id=1, cart_id=10)


def test_store_endpoint(client):
    http, mocks = client
    r = http.get("/statistics/stores/8")
    assert r.status_code == 200
    assert r.json()["total_open_carts"] == 2
    mocks["get_store_statistics"].assert_called_once_with(8)


def test_enterprise_endpoint(client):
    http, mocks = client
    r = http.get("/statistics/enterprises/Example")
    assert r.status_code == 200
    assert r.json()["total_locations"] == 3
    mocks["get_enterprise_statistics"].assert_called_once_with("Example")


@pytest.mark.parametrize("url", [
    "/statistics/users/0",
    "/statistics/users/not-an-int",
    "/statistics/carts/-2/users/1",
    "/statistics/carts/10/users/0",
    "/statistics/stores/0",
])
def test_invalid_path_returns_422(client, url):
    http, _ = client
    assert http.get(url).status_code == 422
