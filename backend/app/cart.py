"""Supabase Cart routes: save as backend/app/cart.py.

Uses app/database.py get_supabase(). No in-memory data or ID counter.
GET requests use the publishable client and are subject to RLS.
Writes are disabled until get_cart_session supplies a verified integer users.userid
and a request-scoped Supabase client carrying the user's access token.
CREATE assumes the database generates cartid; the supplied SQL needs that change.
Do not replace missing authentication with a hardcoded user or a caller-supplied ID.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Response
from httpx import RequestError
from postgrest.exceptions import APIError
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field
from supabase import Client

from .database import get_supabase

# Allowed statuses from the Supabase cart table.
CartStatus = Literal["Active", "Inactive"]


class CartCreate(BaseModel):
    """JSON fields the frontend sends when creating a cart."""
    model_config = ConfigDict(extra="forbid")
    storeid: int = Field(gt=0)
    location: str | None = Field(default=None, max_length=30)
    deadline: AwareDatetime | None = None
    minimumamount: Decimal = Field(ge=0, max_digits=10, decimal_places=2)


class CartUpdate(BaseModel):
    """Omit fields to keep them; location and deadline may be cleared with null."""
    model_config = ConfigDict(extra="forbid")
    location: str | None = Field(default=None, max_length=30)
    deadline: AwareDatetime | None = None
    status: CartStatus | None = None
    minimumamount: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)


class Cart(CartCreate):
    """The full cart returned to the frontend."""
    cartid: int
    owneruserid: int
    status: CartStatus = "Active"
    currentamount: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)


@dataclass
class CartSession:
    db: Client
    user_id: int | None = None


def get_cart_session() -> CartSession:
    # TODO AUTH: replace with the team's verified login dependency.
    # Resolve the auth identity to public.users.userid (an INTEGER, not an auth UUID).
    # Supply a fresh client carrying that user's token so RLS can identify them.
    # Never set user-specific tokens on the shared cached client.
    return CartSession(db=get_supabase())


def require_user(session: CartSession) -> int:
    if session.user_id is None:
        raise HTTPException(
            status_code=501,
            detail="Cart writes await the team's authentication integration",
        )
    return session.user_id


def execute_query(query):
    # Turn known database errors into useful responses without exposing raw details.
    try:
        return query.execute().data
    except APIError as error:
        code = error.code
        if code == "23503":
            raise HTTPException(409, "Related store/user is missing, or related records prevent deletion") from error
        if code == "23505":
            raise HTTPException(409, "A record with this unique value already exists") from error
        if code in {"42501", "PGRST301", "PGRST302"}:
            raise HTTPException(403, "Database access denied; check login, grants and RLS policies") from error
        if code in {"23502", "23514", "22003"}:
            raise HTTPException(422, "Database constraint failed; check values and cart ID generation") from error
        raise HTTPException(503, "Supabase could not complete the request") from error
    except RequestError as error:
        raise HTTPException(503, "Could not reach Supabase") from error


def find_cart(db: Client, cart_id: int) -> Cart:
    rows = execute_query(db.table("cart").select("*").eq("cartid", cart_id).limit(1))
    if not rows:
        raise HTTPException(404, "Cart not found or not visible to this user")
    return Cart(**rows[0])


def check_owner(cart: Cart, user_id: int) -> None:
    if cart.owneruserid != user_id:
        raise HTTPException(403, "Only the owner can change this cart")


router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.post("", response_model=Cart, status_code=201)
def create_cart(body: CartCreate, session: CartSession = Depends(get_cart_session)):
    user_id = require_user(session)
    # mode="json" serializes dates and Decimal values for the HTTP request.
    values = body.model_dump(mode="json")
    values["owneruserid"] = user_id
    # cartid, status and currentamount come from database defaults.
    rows = execute_query(session.db.table("cart").insert(values, returning="representation"))
    if not rows:
        raise HTTPException(502, "Insert returned no cart; check SELECT permissions before retrying")
    return Cart(**rows[0])


@router.get("", response_model=list[Cart])
def get_all_carts(
    status: CartStatus | None = None,
    storeid: int | None = None,
    owneruserid: int | None = None,
    session: CartSession = Depends(get_cart_session),
):
    query = session.db.table("cart").select("*").order("cartid")
    if status is not None:
        query = query.eq("status", status)
    if storeid is not None:
        query = query.eq("storeid", storeid)
    if owneruserid is not None:
        query = query.eq("owneruserid", owneruserid)
    # Fetch pages so the API's default row limit doesn't silently truncate results.
    results = []
    page_size = 100
    offset = 0
    while True:
        rows = execute_query(query.range(offset, offset + page_size - 1))
        results.extend(Cart(**row) for row in rows)
        if len(rows) < page_size:
            return results
        offset += page_size


@router.get("/{cart_id}", response_model=Cart)
def get_cart(
    cart_id: int = Path(gt=0),
    session: CartSession = Depends(get_cart_session),
):
    return find_cart(session.db, cart_id)


@router.patch("/{cart_id}", response_model=Cart)
def update_cart(
    body: CartUpdate,
    cart_id: int = Path(gt=0),
    session: CartSession = Depends(get_cart_session),
):
    user_id = require_user(session)
    cart = find_cart(session.db, cart_id)
    check_owner(cart, user_id)
    changes = body.model_dump(mode="json", exclude_unset=True)
    for field in ("status", "minimumamount"):
        if field in changes and changes[field] is None:
            raise HTTPException(422, f"{field} cannot be null")
    if not changes:
        return cart
    rows = execute_query(
        session.db.table("cart")
        .update(changes, returning="representation")
        .eq("cartid", cart_id)
        .eq("owneruserid", user_id)
    )
    if not rows:
        raise HTTPException(409, "No updated cart returned; check RLS or whether ownership changed")
    return Cart(**rows[0])


@router.delete("/{cart_id}", status_code=204)
def delete_cart(
    cart_id: int = Path(gt=0),
    session: CartSession = Depends(get_cart_session),
):
    user_id = require_user(session)
    cart = find_cart(session.db, cart_id)
    check_owner(cart, user_id)
    # Foreign keys enforce the team's deletion rules; no separate child deletes.
    rows = execute_query(
        session.db.table("cart")
        .delete(returning="representation")
        .eq("cartid", cart_id)
        .eq("owneruserid", user_id)
    )
    if not rows:
        raise HTTPException(409, "No deleted cart returned; check RLS or whether ownership changed")
    return Response(status_code=204)
