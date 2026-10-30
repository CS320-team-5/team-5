import pytest
from pydantic import ValidationError

from app.models.review import ReviewCreate, ReviewUpdate, ReviewResponse


def valid_review():
    return {"targetuserid": 1, "authoruserid": 2, "rating": 5, "commentbody": "Great!"}


def test_create_valid():
    review = ReviewCreate(**valid_review())
    assert review.model_dump() == valid_review()


@pytest.mark.parametrize("field,value", [("targetuserid", 0), ("targetuserid", -1), ("authoruserid", 0), ("authoruserid", -2)])
def test_create_rejects_nonpositive_user_ids(field, value):
    payload = valid_review()
    payload[field] = value
    with pytest.raises(ValidationError):
        ReviewCreate(**payload)


@pytest.mark.parametrize("missing", ["targetuserid", "authoruserid", "rating"])
def test_create_requires_fields(missing):
    payload = valid_review()
    del payload[missing]
    with pytest.raises(ValidationError):
        ReviewCreate(**payload)


@pytest.mark.parametrize("payload", [
    {"targetuserid": 1, "authoruserid": 2, "rating": 5},
    {"targetuserid": 1, "authoruserid": 2, "rating": 5, "commentbody": None},
])
def test_create_optional_comment(payload):
    assert ReviewCreate(**payload).commentbody is None


def test_create_rejects_unknown_field():
    with pytest.raises(ValidationError):
        ReviewCreate(**valid_review(), username="extra")


@pytest.mark.parametrize("payload", [{"rating": 4}, {"commentbody": "Edited"}])
def test_update_allows_partial_fields(payload):
    review = ReviewUpdate(**payload)
    assert review.model_dump(exclude_unset=True) == payload


def test_update_allows_empty_model():
    assert ReviewUpdate().model_dump(exclude_unset=True) == {}


def test_update_rejects_unknown_field():
    with pytest.raises(ValidationError):
        ReviewUpdate(authoruserid=7)


def test_response_accepts_complete_record():
    response = ReviewResponse(reviewid=10, **valid_review())
    assert response.reviewid == 10
    assert response.rating == 5
    assert response.commentbody == "Great!"


def test_response_requires_review_id():
    with pytest.raises(ValidationError):
        ReviewResponse(**valid_review())
