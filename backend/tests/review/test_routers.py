from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.routers import review as review_router
from app.database import get_supabase


@pytest.fixture
def saved_review():
    return {"reviewid": 7, "targetuserid": 1, "authoruserid": 2, "rating": 5, "commentbody": "Great!"}


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(review_router.router)
    fake_db = MagicMock()
    app.dependency_overrides[get_supabase] = lambda: fake_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_post_review_success(client, saved_review, monkeypatch):
    fake = MagicMock(return_value=saved_review)
    monkeypatch.setattr(review_router.service, "create_review", fake)
    payload = {k: v for k, v in saved_review.items() if k != "reviewid"}

    response = client.post("/reviews", json=payload)
    assert response.status_code == 201
    assert response.json() == saved_review
    assert fake.call_args.args[1].model_dump() == payload


@pytest.mark.parametrize("payload", [
    {"authoruserid": 2, "rating": 5},
    {"targetuserid": 0, "authoruserid": 2, "rating": 5},
    {"targetuserid": 1, "authoruserid": 2},
    {"targetuserid": 1, "authoruserid": 2, "rating": 5, "unexpected": True},
])
def test_post_review_invalid(client, payload):
    assert client.post("/reviews", json=payload).status_code == 422


def test_get_reviews_success(client, saved_review, monkeypatch):
    fake = MagicMock(return_value=[saved_review])
    monkeypatch.setattr(review_router.service, "get_reviews", fake)

    response = client.get("/reviews")
    assert response.status_code == 200
    assert response.json() == [saved_review]
    fake.assert_called_once()


def test_get_reviews_empty(client, monkeypatch):
    monkeypatch.setattr(review_router.service, "get_reviews", MagicMock(return_value=[]))
    assert client.get("/reviews").json() == []


def test_get_review_success(client, saved_review, monkeypatch):
    fake = MagicMock(return_value=saved_review)
    monkeypatch.setattr(review_router.service, "get_review", fake)

    response = client.get("/reviews/7")
    assert response.status_code == 200
    assert response.json() == saved_review
    assert fake.call_args.args[1] == 7


@pytest.mark.parametrize("url", ["/reviews/0", "/reviews/-1", "/reviews/not-a-number"])
def test_get_review_invalid_id(client, url):
    assert client.get(url).status_code == 422


def test_get_review_missing(client, monkeypatch):
    monkeypatch.setattr(review_router.service, "get_review", MagicMock(side_effect=HTTPException(404, "Review not found")))
    response = client.get("/reviews/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"


def test_patch_review_success(client, saved_review, monkeypatch):
    updated = {**saved_review, "rating": 4}
    fake = MagicMock(return_value=updated)
    monkeypatch.setattr(review_router.service, "update_review", fake)

    response = client.patch("/reviews/7", json={"rating": 4})
    assert response.status_code == 200
    assert response.json() == updated
    assert fake.call_args.args[1] == 7
    assert fake.call_args.args[2].model_dump(exclude_unset=True) == {"rating": 4}


def test_patch_review_empty(client, monkeypatch):
    monkeypatch.setattr(review_router.service, "update_review", MagicMock(side_effect=HTTPException(400, "No fields provided")))
    response = client.patch("/reviews/7", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "No fields provided"


def test_patch_review_invalid_id(client):
    assert client.patch("/reviews/0", json={"rating": 4}).status_code == 422


def test_patch_review_missing(client, monkeypatch):
    monkeypatch.setattr(review_router.service, "update_review", MagicMock(side_effect=HTTPException(404, "Review not found")))
    assert client.patch("/reviews/999", json={"rating": 4}).status_code == 404


def test_delete_review_success(client, monkeypatch):
    fake = MagicMock(return_value=None)
    monkeypatch.setattr(review_router.service, "delete_review", fake)

    response = client.delete("/reviews/7")
    assert response.status_code == 204
    assert response.content == b""
    assert fake.call_args.args[1] == 7


def test_delete_review_missing(client, monkeypatch):
    monkeypatch.setattr(review_router.service, "delete_review", MagicMock(side_effect=HTTPException(404, "Review not found")))
    assert client.delete("/reviews/999").status_code == 404


def test_delete_review_invalid_id(client):
    assert client.delete("/reviews/0").status_code == 422
