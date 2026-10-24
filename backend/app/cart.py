from decimal import Decimal
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Path, Response
from httpx import RequestError
from postgrest.exceptions import APIError
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field
from supabase import Client
from datetime import datetime, timezone
from .database import get_supabase
from .auth import AuthSession, get_auth_session


CartStatus = Literal["Active", "Inactive"]


class CartCreate(BaseModel):
    """JSON fields the frontend sends when creating a cart."""
    model_config = ConfigDict(extra="forbid")
    storeid: int = Field(gt=0)
    location: str | None = Field(default=None, max_length=30)
    deadline: AwareDatetime 
    minimumamount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class CartUpdate(BaseModel):
    
    model_config = ConfigDict(extra="forbid")
    location: str | None = Field(default=None, max_length=30)
    deadline: AwareDatetime | None = None
    status: CartStatus | None = None
    minimumamount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)


class Cart(CartCreate):
    """The full cart returned to the frontend."""
    cartid: int
    owneruserid: int
    status: CartStatus = "Active"
    currentamount: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)



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

def has_other_participants(db: Client, cart: Cart) -> bool:
    rows = execute_query(
        db.table("cartparticipant")
        .select("userid")
        .eq("cartid", cart.cartid)
        .eq("status", "Active")
        .neq("userid", cart.owneruserid)
        .limit(1)
    )
    return bool(rows)

def has_other_participant_records(db: Client, cart: Cart) -> bool:
    rows = execute_query(
        db.table("cartparticipant")
        .select("userid")
        .eq("cartid", cart.cartid)
        .neq("userid", cart.owneruserid)
        .limit(1)
    )

    return bool(rows)

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.post("", response_model=Cart, status_code=201)
def create_cart(
    body: CartCreate,
    session: AuthSession = Depends(get_auth_session),
):
    if body.deadline <= datetime.now(timezone.utc):
            raise HTTPException(
                422,
                "Deadline must be in the future",
            )
    
    values = body.model_dump(mode="json")

    values["owneruserid"] = session.user_id

    rows = execute_query(
        session.db
        .table("cart")
        .insert(values)
        .select("*")
    )
    
    if not rows:
        raise HTTPException(
            502,
            "Insert returned no cart",
        )

    return Cart(**rows[0])


#gets the previous cart of a user that has a deadline that has passed and returns it in descending order of deadline

@router.get("/history", response_model=list[Cart])
def get_cart_history(
    session: AuthSession = Depends(get_auth_session),
):
    now = datetime.now(timezone.utc).isoformat()

    rows = execute_query(
        session.db.table("cart")
        .select("*")
        .eq("owneruserid", session.user_id)
        .lte("deadline", now)
        .order("deadline", desc=True)
    )

    return [Cart(**row) for row in rows]

@router.get("/{cart_id}", response_model=Cart)
def get_cart(
    cart_id: int = Path(gt=0),
    db: Client = Depends(get_supabase),
):
    return find_cart(db, cart_id)


@router.get("", response_model=list[Cart])
def get_all_carts(
    status: CartStatus | None = None,
    storeid: int | None = None,
    owneruserid: int | None = None,
    location: str | None = None,
    db: Client = Depends(get_supabase),
):
    query = db.table("cart").select("*").order("cartid")

    if status is not None:
        query = query.eq("status", status)

    if storeid is not None:
        query = query.eq("storeid", storeid)

    if owneruserid is not None:
        query = query.eq("owneruserid", owneruserid)

    if location is not None:
        query = query.eq("location", location)

    # Expired carts arent returned as joinable active carts, even if the scheduled status update has not run yet.
    
    if status == "Active":
        query = query.gt(
            "deadline",
            datetime.now(timezone.utc).isoformat(),
        )

    rows = execute_query(query)
    return [Cart(**row) for row in rows]

@router.patch("/{cart_id}", response_model=Cart)
def update_cart(
    body: CartUpdate,
    cart_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    cart = find_cart(session.db, cart_id)

    check_owner(cart, session.user_id)

    changes = body.model_dump(
        mode="json",
        exclude_unset=True,
    )

    for field in ("status", "minimumamount", "deadline"):
        if field in changes and changes[field] is None:
            raise HTTPException(
                422,
                f"{field} cannot be null",
            )

    if not changes:
        return cart
    
    #save the current time in UTC to compare with the cart deadline

    now = datetime.now(timezone.utc)

    # Past carts remain read-only for history.
    if cart.deadline <= now:
        raise HTTPException(
            409,
            "Past carts cannot be edited",
        )

    if "deadline" in changes and body.deadline <= now:
        raise HTTPException(
            422,
            "The new deadline must be in the future",
        )

    others_joined = has_other_participants(session.db, cart)

    # These restrictions apply only when another active user joined.
    if others_joined:
        if (
            "deadline" in changes
            and body.deadline < cart.deadline
        ):
            raise HTTPException(
                409,
                "Cannot shorten the deadline after someone joins",
            )

        if changes.get("status") == "Inactive":
            raise HTTPException(
                409,
                "Cannot close early after someone joins",
            )

        for field in ("location", "minimumamount"):
            if (
                field in changes
                and getattr(body, field) != getattr(cart, field)
            ):
                raise HTTPException(
                    409,
                    f"Cannot change {field} after someone joins",
                )
             
    rows = execute_query(
        session.db
        .table("cart")
        .update(changes)
        .eq("cartid", cart_id)
        .eq("owneruserid", session.user_id)
        .select("*")
    )

    if not rows:
        raise HTTPException(
            409,
            "No updated cart returned",
        )

    return Cart(**rows[0])


@router.delete("/{cart_id}", status_code=204)
def delete_cart(
    cart_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    cart = find_cart(session.db, cart_id)

    check_owner(cart, session.user_id)

    if cart.deadline <= datetime.now(timezone.utc):
        raise HTTPException(
            409,
            "Ended carts are preserved for history and savings tracking",
        )

    if has_other_participant_records(session.db, cart):
        raise HTTPException(
            409,
            "Cannot delete a cart that another user has joined",
        )

    rows = execute_query(
        session.db
        .table("cart")
        .delete()
        .eq("cartid", cart_id)
        .eq("owneruserid", session.user_id)
        .eq("deadline", cart.deadline.isoformat())
        .gt("deadline", datetime.now(timezone.utc).isoformat())
    )

    if not rows:
        raise HTTPException(
            409,
            "Cart changed, expired, or deletion was not permitted",
        )

    return Response(status_code=204)