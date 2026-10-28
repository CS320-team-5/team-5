from fastapi import HTTPException
from ..models.cart import Cart
from datetime import datetime, timezone
from ..dependencies.auth import AuthSession
from ..models.cart import CartCreate
from ..repositories.cart import insert_cart
from ..repositories import cart as cart_repository
from supabase import Client
from ..models.cart import CartStatus
from ..models.cart import CartUpdate
from ..repositories.cart import has_other_participants
from ..repositories.cart import has_other_participant_records
from httpx import RequestError
from postgrest.exceptions import APIError

def _raise_database_error(error: APIError | RequestError):
    if isinstance(error, RequestError):
        raise HTTPException(503, "Could not reach Supabase") from error

    code = error.code

    if code == "23503":
        raise HTTPException(
            409,
            "Related store/user is missing, or related records prevent deletion",
        ) from error

    if code == "23505":
        raise HTTPException(
            409,
            "A record with this unique value already exists",
        ) from error

    if code in {"42501", "PGRST301", "PGRST302"}:
        raise HTTPException(
            403,
            "Database access denied; check login, grants and RLS policies",
        ) from error

    if code in {"23502", "23514", "22003"}:
        raise HTTPException(
            422,
            "Database constraint failed; check values and cart ID generation",
        ) from error

    raise HTTPException(
        503,
        "Supabase could not complete the request",
    ) from error

def check_owner(cart: Cart, user_id: int) -> None:
    if cart.owneruserid != user_id:
        raise HTTPException(403, "Only the owner can change this cart")

def create_cart(body: CartCreate, session: AuthSession) -> Cart:
    if body.deadline <= datetime.now(timezone.utc):
        raise HTTPException(422, "Deadline must be in the future")

    values = body.model_dump(mode="json")
    values["owneruserid"] = session.user_id

    try:
        rows = insert_cart(session.db, values)
    except (APIError, RequestError) as error:
        _raise_database_error(error)

    if not rows:
        raise HTTPException(502, "Insert returned no cart")

    return Cart(**rows[0])

def get_cart_history(session: AuthSession) -> list[Cart]:
    now = datetime.now(timezone.utc).isoformat()

    try:
        rows = cart_repository.get_cart_history(
            session.db,
            session.user_id,
            now,
        )
    except (APIError, RequestError) as error:
        _raise_database_error(error)

    return [Cart(**row) for row in rows]

def find_cart(db: Client, cart_id: int) -> Cart:
    try:
        row = cart_repository.find_cart(db, cart_id)
    except (APIError, RequestError) as error:
        _raise_database_error(error)

    if row is None:
        raise HTTPException(
            404,
            "Cart not found or not visible to this user",
        )

    return Cart(**row)

def get_all_carts(
    db: Client,
    status: CartStatus | None = None,
    storeid: int | None = None,
    owneruserid: int | None = None,
    location: str | None = None,
) -> list[Cart]:
    try:
        rows = cart_repository.get_all_carts(
            db=db,
            status=status,
            storeid=storeid,
            owneruserid=owneruserid,
            location=location,
            now=datetime.now(timezone.utc).isoformat(),
        )
    except (APIError, RequestError) as error:
        _raise_database_error(error)

def get_cart(db: Client, cart_id: int) -> Cart:
    return find_cart(db, cart_id)

def update_cart(
    body: CartUpdate,
    cart_id: int,
    session: AuthSession,
) -> Cart:
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

    try:
        others_joined = has_other_participants(session.db, cart)
    except (APIError, RequestError) as error:
        _raise_database_error(error)

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
             
    try:
        rows = cart_repository.update_cart(
            db=session.db,
            cart_id=cart_id,
            user_id=session.user_id,
            changes=changes,
        )
    except (APIError, RequestError) as error:
        _raise_database_error(error)

    if not rows:
        raise HTTPException(
            409,
            "No updated cart returned",
        )

    return Cart(**rows[0])

def delete_cart(
    cart_id: int,
    session: AuthSession,
) -> None:
    cart = find_cart(session.db, cart_id)

    check_owner(cart, session.user_id)

    if cart.deadline <= datetime.now(timezone.utc):
        raise HTTPException(
            409,
            "Ended carts are preserved for history and savings tracking",
        )

    try:
        others_joined = has_other_participant_records(session.db, cart)
    except (APIError, RequestError) as error:
        _raise_database_error(error)

    if others_joined:
           raise HTTPException(
            409,
            "Cannot delete a cart that another user has joined",
        )
    try:
        rows = cart_repository.delete_cart(
            db=session.db,
            cart=cart,
            user_id=session.user_id,
            now=datetime.now(timezone.utc).isoformat(),
        )
    except (APIError, RequestError) as error:
        _raise_database_error(error)
        
    if not rows:
        raise HTTPException(
            409,
            "Cart changed, expired, or deletion was not permitted",
        )

    return None