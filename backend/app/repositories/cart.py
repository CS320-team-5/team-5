
from postgrest.exceptions import APIError
from supabase import Client
from ..models.cart import Cart

def execute_query(query):
    return query.execute().data

def find_cart(db: Client, cart_id: int) -> dict | None:
    rows = execute_query(
        db.table("cart")
        .select("*")
        .eq("cartid", cart_id)
        .limit(1)
    )

    return rows[0] if rows else None

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

def insert_cart(db: Client, values: dict):
    return execute_query(
        db.table("cart")
        .insert(values)
        .select("*")
    )

def get_cart_history(db: Client, user_id: int, now: str):
    return execute_query(
        db.table("cart")
        .select("*")
        .eq("owneruserid", user_id)
        .lte("deadline", now)
        .order("deadline", desc=True)
    )

def get_all_carts(
    db: Client,
    status: str | None,
    storeid: int | None,
    owneruserid: int | None,
    location: str | None,
    now: str,
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

    if status == "Active":
        query = query.gt("deadline", now)

    return execute_query(query)

def update_cart(
    db: Client,
    cart_id: int,
    user_id: int,
    changes: dict,
):
    return execute_query(
        db.table("cart")
        .update(changes)
        .eq("cartid", cart_id)
        .eq("owneruserid", user_id)
        .select("*")
    )

def delete_cart(
    db: Client,
    cart: Cart,
    user_id: int,
    now: str,
):
    return execute_query(
        db.table("cart")
        .delete()
        .eq("cartid", cart.cartid)
        .eq("owneruserid", user_id)
        .eq("deadline", cart.deadline.isoformat())
        .gt("deadline", now)
    )