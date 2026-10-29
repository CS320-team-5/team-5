import pytest
from pydantic import ValidationError

from app.models.message import MessageCreate, MessageUpdate


@pytest.mark.parametrize("payload", [{"messagetext": ""}, {"messagetext": "   "},
                                      {"messagetext": "x" * 2001},
                                      {"messagetext": "hi", "userid": 3},
                                      {"messagetext": "hi", "cartid": 1}])
def test_invalid_payload(payload):
    with pytest.raises(ValidationError):
        MessageCreate.model_validate(payload)


def test_trims_text():
    assert MessageCreate(messagetext="  hello  ").messagetext == "hello"
    assert MessageUpdate(messagetext="  updated ").messagetext == "updated"
