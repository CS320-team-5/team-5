"""Cart access and message ownership checks; DB RLS remains the final gate."""
from typing import NoReturn
from datetime import datetime, timezone
from ..models.cart import Cart

from fastapi import HTTPException
from httpx import RequestError
from postgrest.exceptions import APIError

from ..dependencies.auth import AuthSession
from ..models.message import Message, MessageCreate, MessageUpdate
from ..repositories import message as repository


def _db_error(error: APIError | RequestError) -> NoReturn:
    if isinstance(error, RequestError):
        raise HTTPException(503, "Could not reach Supabase") from error
    if error.code in {"42501", "PGRST301", "PGRST302"}:
        raise HTTPException(403, "Database access denied") from error
    if error.code == "23503":
        raise HTTPException(409, "Related cart or user not found") from error
    if error.code in {"23502", "23514", "22001"}:
        raise HTTPException(422, "Message violates a database constraint") from error
    raise HTTPException(503, "Supabase could not complete the request") from error


def _access_cart(session: AuthSession, cart_id: int) -> dict:
    try:
        cart = repository.find_cart(session.db, cart_id)
        if cart is None:
            raise HTTPException(404, "Cart not found")
        if cart["owneruserid"] == session.user_id:
            return cart
        if repository.find_active_participant(session.db, cart_id, session.user_id):
            return cart
    except (APIError, RequestError) as error:
        _db_error(error)
    raise HTTPException(403, "Only the owner or active participants can access this cart's messages")


def get_message_carts(session: AuthSession) -> list[Cart]:
    try:
        rows = repository.list_message_carts(session.db, session.user_id)
        return [Cart.model_validate(row) for row in rows]
    except (APIError, RequestError) as error:
        _db_error(error)


def _require_open_cart(cart: dict) -> None:
    if cart.get("status") != "Active":
        raise HTTPException(409, "Cannot send messages to an inactive cart")
    deadline = cart.get("deadline")
    if deadline is None:
        raise HTTPException(409, "Cart deadline is missing")
    if datetime.fromisoformat(str(deadline).replace("Z", "+00:00")) <= datetime.now(timezone.utc):
        raise HTTPException(409, "Cannot send messages after the cart deadline")


def get_cart_messages(session: AuthSession, cart_id: int, limit: int) -> list[Message]:
    _access_cart(session, cart_id)
    try:
        rows = repository.list_cart_messages(session.db, cart_id, limit)
    except (APIError, RequestError) as error:
        _db_error(error)
    return [Message.model_validate(row) for row in rows]


def create_cart_message(session: AuthSession, cart_id: int, body: MessageCreate) -> Message:
    cart = _access_cart(session, cart_id)
    _require_open_cart(cart)
    try:
        row = repository.create_message(session.db, cart_id, session.user_id, body.messagetext)
    except (APIError, RequestError) as error:
        _db_error(error)
    if row is None:
        raise HTTPException(403, "Message insert was not permitted")
    return Message.model_validate(row)


def _own_message(session: AuthSession, message_id: int) -> dict:
    try:
        row = repository.find_message(session.db, message_id)
    except (APIError, RequestError) as error:
        _db_error(error)
    if row is None:
        raise HTTPException(404, "Message not found or not visible")
    # The SQL RLS policy may allow a sender to SELECT an old message in a cart
    # they left. Explicitly check current membership before modification.
    _access_cart(session, row["cartid"])
    if row["userid"] != session.user_id:
        raise HTTPException(403, "You can only change your own messages")
    return row


def update_message(session: AuthSession, message_id: int, body: MessageUpdate) -> Message:
    _own_message(session, message_id)
    try:
        row = repository.update_message(session.db, message_id, session.user_id, body.messagetext)
    except (APIError, RequestError) as error:
        _db_error(error)
    if row is None:
        raise HTTPException(403, "Message update was not permitted")
    return Message.model_validate(row)


def delete_message(session: AuthSession, message_id: int) -> None:
    _own_message(session, message_id)
    try:
        deleted = repository.delete_message(session.db, message_id, session.user_id)
    except (APIError, RequestError) as error:
        _db_error(error)
    if not deleted:
        raise HTTPException(403, "Message delete was not permitted")
