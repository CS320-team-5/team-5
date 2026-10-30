import pytest


@pytest.fixture
def participant_row(user_session):
    """A sample participant belonging to the signed-in user."""
    return {
        "cartid": 1,
        "userid": user_session.user_id,
        "status": "Active",
        "amountcontributed": "10.50",
        "joindate": "2026-10-28",
    }