from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.store import Store, StoreCreate, StoreUpdate

VALID = {
    "enterprisename": "Corner Market",
    "storetype": "Grocery",
    "address": "123 Main Street",
    "minimumorderamount": Decimal("10.50"),
}


def test_create_accepts_valid_fields():
    store = StoreCreate(**VALID)
    assert store.enterprisename == "Corner Market"
    assert store.minimumorderamount == Decimal("10.50")


@pytest.mark.parametrize("missing", list(VALID))
def test_create_requires_every_field(missing):
    values = {key: value for key, value in VALID.items() if key != missing}
    with pytest.raises(ValidationError):
        StoreCreate(**values)


@pytest.mark.parametrize("field", ["enterprisename", "storetype", "address"])
def test_create_rejects_empty_strings(field):
    with pytest.raises(ValidationError):
        StoreCreate(**{**VALID, field: ""})


def test_create_rejects_negative_amount():
    with pytest.raises(ValidationError):
        StoreCreate(**{**VALID, "minimumorderamount": Decimal("-0.01")})


def test_create_rejects_unrecognized_fields():
    with pytest.raises(ValidationError):
        StoreCreate(**VALID, unexpected="value")


def test_update_allows_empty_payload():
    assert StoreUpdate().model_dump(exclude_unset=True) == {}


def test_update_allows_partial_payload():
    update = StoreUpdate(address="456 Oak Road")
    assert update.model_dump(exclude_unset=True) == {"address": "456 Oak Road"}


@pytest.mark.parametrize("field", ["enterprisename", "storetype", "address"])
def test_update_rejects_empty_strings(field):
    with pytest.raises(ValidationError):
        StoreUpdate(**{field: ""})


def test_update_rejects_negative_amount():
    with pytest.raises(ValidationError):
        StoreUpdate(minimumorderamount=-1)


def test_update_accepts_explicit_none_at_model_layer():
    # The service layer, not the Pydantic model, rejects explicit nulls.
    assert StoreUpdate(address=None).model_dump(exclude_unset=True) == {"address": None}


@pytest.mark.parametrize("store_id", [0, -1])
def test_store_rejects_nonpositive_ids(store_id):
    with pytest.raises(ValidationError):
        Store(**VALID, storeid=store_id)


def test_store_accepts_positive_id():
    assert Store(**VALID, storeid=8).storeid == 8
