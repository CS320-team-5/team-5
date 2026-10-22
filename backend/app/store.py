
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Path, Response
from httpx import RequestError
from postgrest.exceptions import APIError
from pydantic import BaseModel, ConfigDict, Field
from supabase import Client

from .database import get_supabase
from .auth import AuthSession, get_auth_session


# Models


class StoreCreate(BaseModel):
    """Fields the frontend sends when creating a store."""
    model_config = ConfigDict(extra="forbid")

    enterprisename: str = Field(min_length=1)
    storetype: str = Field(min_length=1)
    address: str = Field(min_length=1)
    minimumorderamount: Decimal = Field(ge=0)


class StoreUpdate(BaseModel):
    """Only supplied fields are updated."""
    model_config = ConfigDict(extra="forbid")

    enterprisename: str | None = Field(default=None, min_length=1)
    storetype: str | None = Field(default=None, min_length=1)
    address: str | None = Field(default=None, min_length=1)
    minimumorderamount: Decimal | None = Field(default=None, ge=0)


class Store(StoreCreate):
    """Full store record returned to the frontend."""
    storeid: int = Field(gt=0)


# Database error handling


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


# Helper


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


# Router


router = APIRouter(prefix="/api/store", tags=["Store"])


# POST /api/store


@router.post("", response_model=Store, status_code=201)
def create_store(
    body: StoreCreate,
    session: AuthSession = Depends(get_auth_session),
):
    values = body.model_dump(mode="json")

    rows = execute_query(
        session.db
        .table("store")
        .insert(values)
        .select("*")
    )

    if not rows:
        raise HTTPException(502, "Insert returned no store")

    return Store(**rows[0])


# GET /api/store/{store_id}


@router.get("/{store_id}", response_model=Store)
def get_store(
    store_id: int = Path(gt=0),
    db: Client = Depends(get_supabase),
):
    return find_store(db, store_id)


# GET /api/store


@router.get("", response_model=list[Store])
def get_all_stores(
    storetype: str | None = None,
    db: Client = Depends(get_supabase),
):
    query = db.table("store").select("*")

    if storetype is not None:
        query = query.eq("storetype", storetype)

    query = query.order("storeid")

    rows = execute_query(query)

    return [Store(**row) for row in rows]


# PATCH /api/store/{store_id}


@router.patch("/{store_id}", response_model=Store)
def update_store(
    body: StoreUpdate,
    store_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    # Ensure the store exists.
    find_store(session.db, store_id)

    changes = body.model_dump(
        mode="json",
        exclude_unset=True,
    )

    # These columns are required by the Store model.
    for field, value in changes.items():
        if value is None:
            raise HTTPException(
                422, f"{field} cannot be null"
            )

    if not changes:
        return find_store(session.db, store_id)

    rows = execute_query(
        session.db
        .table("store")
        .update(changes)
        .eq("storeid", store_id)
        .select("*")
    )

    if not rows:
        raise HTTPException(409, "No updated store returned")

    return Store(**rows[0])


# DELETE /api/store/{store_id}


@router.delete("/{store_id}", status_code=204)
def delete_store(
    store_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    # Ensure the store exists before attempting deletion.
    find_store(session.db, store_id)

    rows = execute_query(
        session.db
        .table("store")
        .delete()
        .eq("storeid", store_id)
        .select("storeid")
    )

    if not rows:
        raise HTTPException(409, "No deleted store returned")

    return Response(status_code=204)
