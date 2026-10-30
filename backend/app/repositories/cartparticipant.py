from supabase import Client
from decimal import Decimal


#Find a user's participation, including inactive records.
def find_participant(
    db: Client,
    cart_id: int,
    user_id: int,
) -> dict | None:
    rows = (
        db.table("cartparticipant")
        .select("*")
        .eq("cartid", cart_id)
        .eq("userid", user_id)
        .limit(1)
        .execute()
        .data
    )

    return rows[0] if rows else None

#Get the active participants in one cart.
def get_active_participants(
    db: Client,
    cart_id: int,
) -> list[dict]:
    return (
        db.table("cartparticipant")
        .select("*")
        .eq("cartid", cart_id)
        .eq("status", "Active")
        .order("userid")
        .execute()
        .data
    )


#Join a cart and update its total.
def join_cart(
    db: Client,
    cart_id: int,
    amount: Decimal,
) -> dict | None:
    rows = (
        db.rpc(
            "join_cart",
            {
                "p_cartid": cart_id,
                "p_amountcontributed": str(amount),
            },
        )
        .execute()
        .data
    )

    return rows[0] if rows else None


#Update the user's contribution and cart total together
def update_contribution(
    db: Client,
    cart_id: int,
    amount: Decimal,
) -> dict | None:
    
    rows = (
        db.rpc(
            "update_cart_contribution",
            {
                "p_cartid": cart_id,
                "p_amountcontributed": str(amount),
            },
        )
        .execute()
        .data
    )
    return rows[0] if rows else None

#Leave the cart and update ownership and totals together.
def leave_cart(
    db: Client,
    cart_id: int,
) -> dict | None:
    rows = (
        db.rpc(
            "leave_cart",
            {"p_cartid": cart_id},
        )
        .execute()
        .data
    )
    return rows[0] if rows else None