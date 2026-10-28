from supabase import Client


PUBLIC_USER_COLUMNS = "userid,name,location"


def get_user(db: Client, user_id: int) -> dict | None:
    """Fetch a user's public profile fields from Supabase."""

    rows = (
        db.table("users")
        .select(PUBLIC_USER_COLUMNS)
        .eq("userid", user_id)
        .limit(1)
        .execute()
        .data
    )
    return rows[0] if rows else None


def update_user(db: Client, user_id: int, changes: dict) -> dict | None:
    """Update one user's permitted fields and return the public profile."""

    rows = (
        db.table("users")
        .update(changes)
        .eq("userid", user_id)
        .select(PUBLIC_USER_COLUMNS)
        .execute()
        .data
    )
    return rows[0] if rows else None