from types import SimpleNamespace
from unittest.mock import Mock
import pandas as pd
import pytest
from fastapi import HTTPException
from app.services import statistics_service as svc


def response(rows):
    return SimpleNamespace(data=rows)


@pytest.fixture
def reviews(monkeypatch):
    rows = [
        {"targetuserid": 1, "rating": 5},
        {"targetuserid": 1, "rating": 3},
        {"targetuserid": 2, "rating": 1},
    ]
    monkeypatch.setattr(svc, "get_review_table", Mock(return_value=response(rows)))


@pytest.fixture
def participants(monkeypatch):
    rows = [
        {"cartid": 10, "userid": 1, "amountcontributed": 20.0},
        {"cartid": 10, "userid": 2, "amountcontributed": 80.0},
        {"cartid": 11, "userid": 1, "amountcontributed": 40.0},
        {"cartid": 12, "userid": 3, "amountcontributed": 100.0},
    ]
    monkeypatch.setattr(svc, "get_cart_participants_table", Mock(return_value=response(rows)))


@pytest.fixture
def carts(monkeypatch):
    rows = [
        {"cartid": 10, "storeid": 8, "status": "open"},
        {"cartid": 11, "storeid": 8, "status": "closed"},
        {"cartid": 12, "storeid": 9, "status": "open"},
        {"cartid": 13, "storeid": 8, "status": "open"},
    ]
    monkeypatch.setattr(svc, "get_carts_table", Mock(return_value=response(rows)))


def test_union_removes_duplicate_rows():
    result = svc.union(pd.DataFrame({"x": [1, 2]}), pd.DataFrame({"x": [2, 3]}))
    assert result["x"].tolist() == [1, 2, 3]


def test_join_matches_shared_cart_id():
    result = svc.join(pd.DataFrame({"cartid": [10], "storeid": [8]}),
                      pd.DataFrame({"cartid": [10], "amountcontributed": [20]}), on="cartid")
    assert result.loc[0, "amountcontributed"] == 20
    assert result.loc[0, "storeid"] == 8


def test_to_dataframe():
    assert svc.to_dataframe(response([{"x": 1}])).loc[0, "x"] == 1


def test_average_rating_filters_target_user(reviews):
    assert svc.avg_rating_of_a_user(1) == pytest.approx(4.0)
    assert svc.avg_rating_of_a_user(99) is None


def test_average_rating_empty(monkeypatch):
    monkeypatch.setattr(svc, "get_review_table", lambda: response([]))
    assert svc.avg_rating_of_a_user(1) is None


def test_contribution_to_specific_cart(participants):
    assert svc.total_spendings_by_user_in_cart(1, 10) == pytest.approx(20.0)
    assert svc.total_spendings_by_user_in_cart(1, 99) == 0.0


def test_user_spending_and_average(participants):
    assert svc.total_spending_of_user(1) == pytest.approx(60.0)
    assert svc.average_contribution_by_user(1) == pytest.approx(30.0)
    assert svc.average_contribution_by_user(99) is None


def test_empty_participants(monkeypatch):
    monkeypatch.setattr(svc, "get_cart_participants_table", lambda *a, **kw: response([]))
    assert svc.total_spending_of_user(1) == 0.0
    assert svc.average_contribution_by_user(1) is None
    assert svc.total_spendings_by_user_in_cart(1, 10) == 0.0


def test_enterprise_locations(monkeypatch):
    monkeypatch.setattr(svc, "get_stores_table", lambda name: response([
        {"enterprisename": "A"}, {"enterprisename": "A"},
        {"enterprisename": "B"},
    ]))
    assert svc.total_number_of_locations_per_enterprise("A") == 2
    assert svc.total_number_of_locations_per_enterprise("Missing") == 0


def test_open_carts_filter_store_and_status(carts):
    assert svc.total_open_carts_by_store(8) == 2
    assert svc.total_open_carts_by_store(9) == 1


def test_total_spending_at_store(carts, participants):
    assert svc.total_spending_at_store(8) == pytest.approx(140.0)
    assert svc.total_spending_at_store(9) == pytest.approx(100.0)


def test_service_error_handler_value_error():
    with pytest.raises(HTTPException) as exc:
        svc.error_handler(ValueError("invalid input"))
    assert exc.value.status_code == 400


def test_service_error_handler_preserves_http_exception():
    original = HTTPException(status_code=404, detail="missing")
    with pytest.raises(HTTPException) as exc:
        svc.error_handler(original)
    assert exc.value is original


def test_service_error_handler_unexpected_error():
    with pytest.raises(HTTPException) as exc:
        svc.error_handler(RuntimeError("failure"))
    assert exc.value.status_code == 500


def test_user_response_builder(monkeypatch):
    monkeypatch.setattr(svc, "total_spending_of_user", lambda uid: 60.0)
    monkeypatch.setattr(svc, "average_contribution_by_user", lambda uid: 30.0)
    monkeypatch.setattr(svc, "avg_rating_of_a_user", lambda uid: 4.0)
    model = svc.get_user_statistics(1)
    assert model.model_dump() == {
        "user_id": 1, "total_spending": 60.0,
        "average_contribution": 30.0, "average_rating": 4.0,
    }


def test_cart_response_builder(monkeypatch):
    monkeypatch.setattr(svc, "total_spendings_by_user_in_cart", lambda uid, cid: 20.0)
    model = svc.get_user_cart_statistics(1, 10)
    assert model.cart_id == 10 and model.user_id == 1
    assert model.total_contribution == 20.0


def test_store_response_builder(monkeypatch):
    monkeypatch.setattr(svc, "total_open_carts_by_store", lambda sid: 2)
    monkeypatch.setattr(svc, "total_spending_at_store", lambda sid: 140.0)
    model = svc.get_store_statistics(8)
    assert model.total_open_carts == 2 and model.total_spending == 140.0


def test_enterprise_response_builder(monkeypatch):
    monkeypatch.setattr(svc, "total_number_of_locations_per_enterprise", lambda name: 2)
    model = svc.get_enterprise_statistics("A")
    assert model.enterprise_name == "A" and model.total_locations == 2
