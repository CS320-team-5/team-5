from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.dependencies.auth import get_auth_session
from app.database import get_supabase
from app.routers.store import router


class FakeResult:
    def __init__(self, data):
        self.data = data


class FakeTableQuery:
    def __init__(self, database):
        self.database = database
        self.operation = "select"
        self.payload = None
        self.filters = []
        self.order_field = None
        self.limit_count = None
        self.selected = "*"

    def select(self, columns):
        self.selected = columns
        return self

    def insert(self, payload):
        self.operation = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.operation = "update"
        self.payload = payload
        return self

    def delete(self):
        self.operation = "delete"
        return self

    def eq(self, column, value):
        self.filters.append((column, value))
        return self

    def order(self, column):
        self.order_field = column
        return self

    def limit(self, count):
        self.limit_count = count
        return self

    def execute(self):
        rows = self.database.rows
        matching = [row for row in rows if all(row.get(k) == v for k, v in self.filters)]
        if self.operation == "insert":
            created = dict(self.payload)
            created["storeid"] = self.database.next_id
            self.database.next_id += 1
            rows.append(created)
            matching = [created]
        elif self.operation == "update":
            for row in matching:
                row.update(self.payload)
        elif self.operation == "delete":
            self.database.rows = [row for row in rows if row not in matching]
        else:
            if self.order_field:
                matching.sort(key=lambda row: row[self.order_field])
            if self.limit_count is not None:
                matching = matching[:self.limit_count]
        return FakeResult([
            dict(row) if self.selected == "*" else
            {key: row[key] for key in self.selected.split(",")}
            for row in matching
        ])


class FakeDatabase:
    def __init__(self):
        self.rows = []
        self.next_id = 1

    def table(self, name):
        assert name == "store"
        return FakeTableQuery(self)


@pytest.fixture
def app_client():
    db = FakeDatabase()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_supabase] = lambda: db
    app.dependency_overrides[get_auth_session] = lambda: SimpleNamespace(db=db)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


STORE = {"enterprisename": "Corner Market", "storetype": "Grocery",
         "address": "123 Main Street", "minimumorderamount": "10.50"}


def create(client, **changes):
    response = client.post("/api/store", json={**STORE, **changes})
    assert response.status_code == 201, response.text
    return response.json()["storeid"]


def test_create_then_read(app_client):
    store_id = create(app_client)
    response = app_client.get(f"/api/store/{store_id}")
    assert response.status_code == 200
    assert response.json()["enterprisename"] == "Corner Market"


def test_create_update_then_read(app_client):
    store_id = create(app_client)
    patch = app_client.patch(f"/api/store/{store_id}", json={"address": "456 Oak Road"})
    assert patch.status_code == 200
    assert patch.json()["address"] == "456 Oak Road"
    assert app_client.get(f"/api/store/{store_id}").json()["address"] == "456 Oak Road"


def test_create_delete_then_not_found(app_client):
    store_id = create(app_client)
    deleted = app_client.delete(f"/api/store/{store_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert app_client.get(f"/api/store/{store_id}").status_code == 404


def test_create_appears_in_listing(app_client):
    first_id = create(app_client)
    second_id = create(app_client, enterprisename="Another Market")
    response = app_client.get("/api/store")
    assert response.status_code == 200
    assert [store["storeid"] for store in response.json()] == [first_id, second_id]


def test_storetype_filter_across_layers(app_client):
    create(app_client, storetype="Grocery")
    create(app_client, storetype="Bakery")
    response = app_client.get("/api/store?storetype=Bakery")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["storetype"] == "Bakery"


def test_invalid_create_returns_422_without_inserting(app_client):
    response = app_client.post("/api/store", json={**STORE, "minimumorderamount": -5})
    assert response.status_code == 422
    assert app_client.get("/api/store").json() == []


def test_patch_with_null_is_rejected_without_mutating(app_client):
    store_id = create(app_client)
    response = app_client.patch(f"/api/store/{store_id}", json={"address": None})
    assert response.status_code == 422
    assert app_client.get(f"/api/store/{store_id}").json()["address"] == STORE["address"]
