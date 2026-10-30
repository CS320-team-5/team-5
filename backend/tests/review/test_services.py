from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.review import ReviewCreate, ReviewUpdate
from app.services import review as service


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def saved_review():
    return {"reviewid": 7, "targetuserid": 1, "authoruserid": 2, "rating": 5, "commentbody": "Great!"}


def test_create_review(db, saved_review, monkeypatch):
    fake_create = MagicMock(return_value=[saved_review])
    monkeypatch.setattr(service.repo, "create_review", fake_create)
    payload = ReviewCreate(targetuserid=1, authoruserid=2, rating=5, commentbody="Great!")

    assert service.create_review(db, payload) == saved_review
    fake_create.assert_called_once_with(db, payload.model_dump())


def test_get_reviews(db, saved_review, monkeypatch):
    expected = [saved_review, {**saved_review, "reviewid": 8}]
    fake_get = MagicMock(return_value=expected)
    monkeypatch.setattr(service.repo, "get_reviews", fake_get)

    assert service.get_reviews(db) == expected
    fake_get.assert_called_once_with(db)


def test_get_review_found(db, saved_review, monkeypatch):
    fake_get = MagicMock(return_value=[saved_review])
    monkeypatch.setattr(service.repo, "get_review", fake_get)

    assert service.get_review(db, 7) == saved_review
    fake_get.assert_called_once_with(db, 7)


def test_get_review_missing(db, monkeypatch):
    monkeypatch.setattr(service.repo, "get_review", MagicMock(return_value=[]))
    with pytest.raises(HTTPException) as exc:
        service.get_review(db, 999)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Review not found"


def test_update_review_success(db, saved_review, monkeypatch):
    updated = {**saved_review, "rating": 4}
    fake_get = MagicMock(return_value=[saved_review])
    fake_update = MagicMock(return_value=[updated])
    monkeypatch.setattr(service.repo, "get_review", fake_get)
    monkeypatch.setattr(service.repo, "update_review", fake_update)

    assert service.update_review(db, 7, ReviewUpdate(rating=4)) == updated
    fake_get.assert_called_once_with(db, 7)
    fake_update.assert_called_once_with(db, 7, {"rating": 4})


def test_update_review_no_fields(db, monkeypatch):
    fake_update = MagicMock()
    fake_get = MagicMock()
    monkeypatch.setattr(service.repo, "update_review", fake_update)
    monkeypatch.setattr(service.repo, "get_review", fake_get)

    with pytest.raises(HTTPException) as exc:
        service.update_review(db, 7, ReviewUpdate())
    assert exc.value.status_code == 400
    assert exc.value.detail == "No fields provided"
    fake_get.assert_not_called()
    fake_update.assert_not_called()


def test_update_review_missing_before_update(db, monkeypatch):
    fake_update = MagicMock()
    monkeypatch.setattr(service.repo, "get_review", MagicMock(return_value=[]))
    monkeypatch.setattr(service.repo, "update_review", fake_update)

    with pytest.raises(HTTPException) as exc:
        service.update_review(db, 999, ReviewUpdate(rating=4))
    assert exc.value.status_code == 404
    fake_update.assert_not_called()


def test_update_review_returns_no_rows(db, saved_review, monkeypatch):
    monkeypatch.setattr(service.repo, "get_review", MagicMock(return_value=[saved_review]))
    monkeypatch.setattr(service.repo, "update_review", MagicMock(return_value=[]))

    with pytest.raises(HTTPException) as exc:
        service.update_review(db, 7, ReviewUpdate(rating=4))
    assert exc.value.status_code == 404


def test_update_explicit_null_is_included(db, saved_review, monkeypatch):
    fake_update = MagicMock(return_value=[{**saved_review, "commentbody": None}])
    monkeypatch.setattr(service.repo, "get_review", MagicMock(return_value=[saved_review]))
    monkeypatch.setattr(service.repo, "update_review", fake_update)

    service.update_review(db, 7, ReviewUpdate(commentbody=None))
    fake_update.assert_called_once_with(db, 7, {"commentbody": None})


def test_delete_review_success(db, saved_review, monkeypatch):
    fake_get = MagicMock(return_value=[saved_review])
    fake_delete = MagicMock(return_value=[saved_review])
    monkeypatch.setattr(service.repo, "get_review", fake_get)
    monkeypatch.setattr(service.repo, "delete_review", fake_delete)

    assert service.delete_review(db, 7) is None
    fake_get.assert_called_once_with(db, 7)
    fake_delete.assert_called_once_with(db, 7)


def test_delete_review_missing(db, monkeypatch):
    fake_delete = MagicMock()
    monkeypatch.setattr(service.repo, "get_review", MagicMock(return_value=[]))
    monkeypatch.setattr(service.repo, "delete_review", fake_delete)

    with pytest.raises(HTTPException) as exc:
        service.delete_review(db, 999)
    assert exc.value.status_code == 404
    fake_delete.assert_not_called()


def test_delete_review_returns_no_rows(db, saved_review, monkeypatch):
    monkeypatch.setattr(service.repo, "get_review", MagicMock(return_value=[saved_review]))
    monkeypatch.setattr(service.repo, "delete_review", MagicMock(return_value=[]))

    with pytest.raises(HTTPException) as exc:
        service.delete_review(db, 7)
    assert exc.value.status_code == 404
