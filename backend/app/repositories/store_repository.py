from fastapi import HTTPException
from httpx import RequestError
from postgrest.exceptions import APIError
from supabase import Client

from ..models.store import Store


def execute_query(query):
    try:
        return query.execute().data

    except APIError as error:
        code = error.code

        if code == "23503":
            raise HTTPException(
                409, "Related records prevent this operation"
            ) from error

        if code == "23505":
            raise HTTPException(
                409, "A record with this unique value already exists"
            ) from error

        if code in {"42501", "PGRST301", "PGRST302"}:
            raise HTTPException(
                403, "Database access denied; check permissions and RLS"
            ) from error

        if code in {"23502", "23514", "22003"}:
            raise HTTPException(
                422, "Store values violate a database constraint"
            ) from error

        raise HTTPException(
            503, "Supabase could not complete the request"
        ) from error

    except RequestError as error:
        raise HTTPException(
            503, "Could not reach Supabase"
        ) from error


def find_store(db: Client, store_id: int) -> Store:
    rows = execute_query(
        db.table("store")
        .select("*")
        .eq("storeid", store_id)
        .limit(1)
    )

    if not rows:
        raise HTTPException(404, "Store not found or not visible")

    return Store(**rows[0])


def create_store_record(db: Client, values: dict):
    return execute_query(
        db.table("store").insert(values).select("*")
    )


def get_all_store_records(db: Client, storetype: str | None = None):
    query = db.table("store").select("*")

    if storetype is not None:
        query = query.eq("storetype", storetype)

    return execute_query(query.order("storeid"))


def update_store_record(db: Client, store_id: int, changes: dict):
    return execute_query(
        db.table("store")
        .update(changes)
        .eq("storeid", store_id)
        .select("*")
    )


def delete_store_record(db: Client, store_id: int):
    return execute_query(
        db.table("store")
        .delete()
        .eq("storeid", store_id)
        .select("storeid")
    )