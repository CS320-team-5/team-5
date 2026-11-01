
from fastapi import HTTPException
from supabase import Client

from ..repositories import review_repository as repo
from ..models.review import ReviewCreate, ReviewUpdate


def create_review(db: Client, review: ReviewCreate):
    data = review.model_dump()
    result = repo.create_review(db, data)
    return result[0]


def get_reviews(db: Client):
    return repo.get_reviews(db)


def get_review(db: Client, review_id: int):
    result = repo.get_review(db, review_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    return result[0]


def update_review(
    db: Client,
    review_id: int,
    review: ReviewUpdate
):
    data = review.model_dump(exclude_unset=True)

    if not data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided"
        )

    get_review(db, review_id)

    result = repo.update_review(db, review_id, data)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    return result[0]


def delete_review(db: Client, review_id: int):
    get_review(db, review_id)

    result = repo.delete_review(db, review_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )
