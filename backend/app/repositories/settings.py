from supabase import Client

from ..models.settings import UserSettings


def get_user_settings(db: Client, auth_id: str) -> UserSettings:
    result = (
        db.table("user_settings")
        .select("courier_arrival_sms, nearby_cart_alerts, member_direct_chat_alerts")
        .eq("authid", auth_id)
        .limit(1)
        .execute()
    )

    if not result.data:
        return UserSettings()

    return UserSettings.model_validate(result.data[0])

def update_user_settings(
    db: Client, auth_id: str, changes: dict[str, bool]
) -> UserSettings:
    if not changes:
        return get_user_settings(db, auth_id)

    result = (
        db.table("user_settings")
        .upsert(
            {"authid": auth_id, **changes},
            on_conflict="authid",
            default_to_null=False,
        )
        .execute()
    )
    if not result.data:
        raise RuntimeError("Settings save returned no row")
    return UserSettings.model_validate(result.data[0])