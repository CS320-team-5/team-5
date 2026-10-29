"""Supabase queries; deliberately uses the existing table and column names."""
from supabase import Client


def find_cart(db: Client, cart_id: int) -> dict | None:
    rows = (db.table("cart").select("cartid,owneruserid")
            .eq("cartid", cart_id).limit(1).execute().data)
    return rows[0] if rows else None


def find_active_participant(db: Client, cart_id: int, user_id: int) -> bool:
    rows = (db.table("cartparticipant").select("userid")
            .eq("cartid", cart_id).eq("userid", user_id)
            .eq("status", "Active").limit(1).execute().data)
    return bool(rows)


def list_cart_messages(db: Client, cart_id: int, limit: int) -> list[dict]:
    # Query the newest messages and return them in chronological order for chat UI.
    rows = (db.table("message")
            .select("messageid,cartid,userid,messagetext,timestamp")
            .eq("cartid", cart_id)
            .order("timestamp", desc=True)
            .order("messageid", desc=True)
            .limit(limit).execute().data)
    return list(reversed(rows))


def create_message(db: Client, cart_id: int, user_id: int, text: str) -> dict | None:
    rows = (db.table("message")
            .insert({"cartid": cart_id, "userid": user_id, "messagetext": text})
            .select("messageid,cartid,userid,messagetext,timestamp")
            .execute().data)
    return rows[0] if rows else None


def find_message(db: Client, message_id: int) -> dict | None:
    rows = (db.table("message")
            .select("messageid,cartid,userid,messagetext,timestamp")
            .eq("messageid", message_id).limit(1).execute().data)
    return rows[0] if rows else None


def update_message(db: Client, message_id: int, user_id: int, text: str) -> dict | None:
    rows = (db.table("message").update({"messagetext": text})
            .eq("messageid", message_id).eq("userid", user_id)
            .select("messageid,cartid,userid,messagetext,timestamp")
            .execute().data)
    return rows[0] if rows else None


def delete_message(db: Client, message_id: int, user_id: int) -> bool:
    rows = (db.table("message").delete()
            .eq("messageid", message_id).eq("userid", user_id)
            .select("messageid").execute().data)
    return bool(rows)
