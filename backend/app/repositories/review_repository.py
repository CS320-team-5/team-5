
from supabase import Client

TABLE = "review"


def create_review(db: Client, data: dict):
    return (
        db.table(TABLE)
        .insert(data)
        .execute()
        .data
    )


def get_reviews(db: Client):
    return (
        db.table(TABLE)
        .select("*")
        .execute()
        .data
    )


def get_review(db: Client, review_id: int):
    return (
        db.table(TABLE)
        .select("*")
        .eq("reviewid", review_id)
        .execute()
        .data
    )


def update_review(db: Client, review_id: int, data: dict):
    return (
        db.table(TABLE)
        .update(data)
        .eq("reviewid", review_id)
        .execute()
        .data
    )


def delete_review(db: Client, review_id: int):
    return (
        db.table(TABLE)
        .delete()
        .eq("reviewid", review_id)
        .execute()
        .data
    )
