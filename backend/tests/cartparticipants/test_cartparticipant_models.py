import pytest
from pydantic import ValidationError
from app.models.cartparticipant import ParticipantJoin, ParticipantUpdate
from decimal import Decimal
# Checks that joining without an amount starts the contribution at zero.
def test_join_defaults_to_zero():
    participant = ParticipantJoin()

    assert participant.amountcontributed == Decimal("0.00")


# Checks that valid contribution amounts are accepted.
@pytest.mark.parametrize("amount", ["0.00", "10.50"])
def test_join_accepts_valid_amount(amount):
    participant = ParticipantJoin(amountcontributed=amount)

    assert participant.amountcontributed == Decimal(amount)


# Checks that negative contributions are rejected.
@pytest.mark.parametrize("model", [ParticipantJoin, ParticipantUpdate])
def test_negative_contribution_is_rejected(model):
    with pytest.raises(ValidationError):
        model(amountcontributed="-1.00")


# Checks that amounts cannot contain fractions smaller than one cent.
@pytest.mark.parametrize("model", [ParticipantJoin, ParticipantUpdate])
def test_extra_decimal_places_are_rejected(model):
    with pytest.raises(ValidationError):
        model(amountcontributed="10.555")


# Checks that an update must include the new amount.
def test_update_requires_amount():
    with pytest.raises(ValidationError):
        ParticipantUpdate()


# Checks that the frontend cannot choose another user's identity.
@pytest.mark.parametrize("model", [ParticipantJoin, ParticipantUpdate])
def test_user_id_cannot_be_supplied(model):
    with pytest.raises(ValidationError):
        model(amountcontributed="10.00", userid=2)


# Checks that the frontend cannot choose its participation status.
def test_join_cannot_supply_status():
    with pytest.raises(ValidationError):
        ParticipantJoin(
            amountcontributed="10.00",
            status="Inactive",
        )