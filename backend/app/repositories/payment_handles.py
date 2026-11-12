from supabase import Client

from ..models.payment_handles import PaymentHandles


def get_payment_handles(db: Client, auth_id: str) -> PaymentHandles:
    result = (
        db.table("user_payment_handles")
        .select("venmo_handle,zelle_identifier,cash_app_handle")
        .eq("authid", auth_id)
        .limit(1)
        .execute()
    )
    return PaymentHandles.model_validate(result.data[0]) if result.data else PaymentHandles()


def update_payment_handles(
    db: Client, auth_id: str, changes: dict[str, str | None]
) -> PaymentHandles:
    if not changes:
        return get_payment_handles(db, auth_id)

    result = (
        db.table("user_payment_handles")
        .upsert(
            {**changes, "authid": auth_id},
            on_conflict="authid",
            default_to_null=False,
        )
        .execute()
    )

    if not result.data:
        raise RuntimeError("Payment handle save returned no row")

    return PaymentHandles.model_validate(result.data[0])