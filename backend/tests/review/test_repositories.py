from unittest.mock import MagicMock
import pytest

from app.repositories import review_repository as repo


@pytest.fixture
def db():
    return MagicMock()


def test_create_review(db):
    payload = {"targetuserid": 1, "authoruserid": 2, "rating": 5}
    expected = [{"reviewid": 3, **payload}]
    db.table.return_value.insert.return_value.execute.return_value.data = expected

    assert repo.create_review(db, payload) == expected
    db.table.assert_called_once_with("review")
    db.table.return_value.insert.assert_called_once_with(payload)
    db.table.return_value.insert.return_value.execute.assert_called_once_with()


def test_get_reviews(db):
    expected = [{"reviewid": 1}, {"reviewid": 2}]
    db.table.return_value.select.return_value.execute.return_value.data = expected

    assert repo.get_reviews(db) == expected
    db.table.assert_called_once_with("review")
    db.table.return_value.select.assert_called_once_with("*")
    db.table.return_value.select.return_value.execute.assert_called_once_with()


def test_get_review(db):
    expected = [{"reviewid": 7}]
    db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = expected

    assert repo.get_review(db, 7) == expected
    db.table.assert_called_once_with("review")
    db.table.return_value.select.assert_called_once_with("*")
    db.table.return_value.select.return_value.eq.assert_called_once_with("reviewid", 7)
    db.table.return_value.select.return_value.eq.return_value.execute.assert_called_once_with()


def test_update_review(db):
    payload = {"rating": 4}
    expected = [{"reviewid": 7, "rating": 4}]
    db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = expected

    assert repo.update_review(db, 7, payload) == expected
    db.table.assert_called_once_with("review")
    db.table.return_value.update.assert_called_once_with(payload)
    db.table.return_value.update.return_value.eq.assert_called_once_with("reviewid", 7)
    db.table.return_value.update.return_value.eq.return_value.execute.assert_called_once_with()


def test_delete_review(db):
    expected = [{"reviewid": 7}]
    db.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = expected

    assert repo.delete_review(db, 7) == expected
    db.table.assert_called_once_with("review")
    db.table.return_value.delete.assert_called_once_with()
    db.table.return_value.delete.return_value.eq.assert_called_once_with("reviewid", 7)
    db.table.return_value.delete.return_value.eq.return_value.execute.assert_called_once_with()


def test_get_reviews_empty(db):
    db.table.return_value.select.return_value.execute.return_value.data = []
    assert repo.get_reviews(db) == []
