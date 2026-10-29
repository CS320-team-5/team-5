from fastapi import HTTPException
from httpx import RequestError
from postgrest.exceptions import APIError
from ..dependencies.auth import AuthSession
from ..models.cartparticipant import CartParticipant, ParticipantJoin, ParticipantUpdate
from ..repositories import cartparticipant as participant_repository
from . import cart as cart_service

# Confirm the cart exists and is visible to this user.
def get_active_participants(
    cart_id: int,
    session: AuthSession,
) -> list[CartParticipant]:
    cart_service.get_cart(
        db=session.db,
        cart_id=cart_id,
    )
    try:
        rows = participant_repository.get_active_participants(
            session.db,
            cart_id,
        )

    except APIError as error:
        if error.code in {"42501", "PGRST301", "PGRST302"}:
            raise HTTPException(
                403,
                "Not permitted to view these participants",
            ) from error

        raise HTTPException(
            503,
            "Could not retrieve cart participants",
        ) from error
    
    except RequestError as error:
        raise HTTPException(
            503,
            "Could not reach Supabase",
        ) from error

    return [CartParticipant(**row) for row in rows]

def _raise_database_error(error: APIError | RequestError) -> None:
    if isinstance(error, RequestError):
        raise HTTPException(503, "Could not reach Supabase") from error

    if error.code == "P0002":
        raise HTTPException(404, "Cart not found") from error

    if error.code == "P0001":
        raise HTTPException(
            409,
            "The action conflicts with the cart or participation state",
        ) from error
    
    if error.code in {"42501", "PGRST301", "PGRST302"}:
        raise HTTPException(403, "Database access denied") from error

    if error.code in {"23502", "23514", "22003"}:
        raise HTTPException(422, "Invalid participant information") from error

    raise HTTPException(503, "Could not complete participant request") from error

def join_cart(
    cart_id: int,
    body: ParticipantJoin,
    session: AuthSession,
) -> CartParticipant:
    try:
        row = participant_repository.join_cart(
            db=session.db,
            cart_id=cart_id,
            amount=body.amountcontributed,
        )
    except (APIError, RequestError) as error:
        _raise_database_error(error)

    if row is None:
        raise HTTPException(502, "Join returned no participant")

    return CartParticipant(**row)


def update_contribution(
    cart_id: int,
    body: ParticipantUpdate,
    session: AuthSession,
) -> CartParticipant:
    try:
        row = participant_repository.update_contribution(
            db=session.db,
            cart_id=cart_id,
            amount=body.amountcontributed,
        )
    except (APIError, RequestError) as error:
        _raise_database_error(error)

    if row is None:
        raise HTTPException(
            502,
            "Contribution update returned no participant",
        )
    return CartParticipant(**row)

def leave_cart(
    cart_id: int,
    session: AuthSession,
) -> None:
    try:
        row = participant_repository.leave_cart(
            db=session.db,
            cart_id=cart_id,
        )
    except (APIError, RequestError) as error:
        _raise_database_error(error)
    if row is None:
        raise HTTPException(
            502,
            "Leave returned no participant",
        )