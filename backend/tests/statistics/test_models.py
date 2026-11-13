import pytest
from pydantic import ValidationError
from app.models.statistics import (
    StatisticsUserResponse, StatisticsCartResponse,
    StatisticsStoreResponse, StatisticsEnterpriseResponse,
)


def test_user_response_valid_and_nullable_fields():
    result = StatisticsUserResponse(user_id=1, total_spending=25.5)
    assert result.average_rating is None
    assert result.average_contribution is None
    assert result.model_dump()["total_spending"] == 25.5


@pytest.mark.parametrize("values", [
    {"user_id": 0, "total_spending": 1},
    {"user_id": 1, "total_spending": -1},
    {"user_id": 1, "total_spending": 1, "unknown": True},
])
def test_user_response_rejects_invalid_values(values):
    with pytest.raises(ValidationError):
        StatisticsUserResponse(**values)


def test_cart_response_valid():
    result = StatisticsCartResponse(cart_id=2, user_id=1, total_contribution=12.5)
    assert result.total_contribution == 12.5


@pytest.mark.parametrize("values", [
    {"cart_id": 0, "user_id": 1, "total_contribution": 5},
    {"cart_id": 1, "user_id": -1, "total_contribution": 5},
    {"cart_id": 1, "user_id": 1, "total_contribution": -5},
])
def test_cart_response_rejects_invalid_values(values):
    with pytest.raises(ValidationError):
        StatisticsCartResponse(**values)


def test_store_response_valid():
    result = StatisticsStoreResponse(store_id=3, total_open_carts=2, total_spending=17)
    assert result.total_open_carts == 2


def test_store_response_rejects_negative_counts():
    with pytest.raises(ValidationError):
        StatisticsStoreResponse(store_id=3, total_open_carts=-1, total_spending=0)


def test_enterprise_response_valid():
    result = StatisticsEnterpriseResponse(enterprise_name="Example", total_locations=4)
    assert result.total_locations == 4


def test_enterprise_response_rejects_negative_locations():
    with pytest.raises(ValidationError):
        StatisticsEnterpriseResponse(enterprise_name="Example", total_locations=-1)
