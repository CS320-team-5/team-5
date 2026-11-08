
from fastapi import APIRouter, Depends, Path, Response
from supabase import Client

from ..database import get_supabase
from ..models.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
)
from ..services import review as service


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=201
)
def create_review(
    review: ReviewCreate,
    db: Client = Depends(get_supabase)
):
    return service.create_review(db, review)


@router.get(
    "",
    response_model=list[ReviewResponse]
)
def get_reviews(db: Client = Depends(get_supabase)):
    return service.get_reviews(db)


@router.get(
    "/{review_id}",
    response_model=ReviewResponse
)
def get_review(
    review_id: int = Path(gt=0),
    db: Client = Depends(get_supabase)
):
    return service.get_review(db, review_id)


@router.patch(
    "/{review_id}",
    response_model=ReviewResponse
)
def update_review(
    review: ReviewUpdate,
    review_id: int = Path(gt=0),
    db: Client = Depends(get_supabase)
):
    return service.update_review(db, review_id, review)


@router.delete(
    "/{review_id}",
    status_code=204
)
def delete_review(
    review_id: int = Path(gt=0),
    db: Client = Depends(get_supabase)
):
    service.delete_review(db, review_id)
    return Response(status_code=204)
