from fastapi import APIRouter, Depends, Path, Query, Response

from ..dependencies.auth import AuthSession, get_auth_session
from ..models.message import Message, MessageCreate, MessageUpdate
from ..services import message as service

router = APIRouter(prefix="/api/message", tags=["Message"])


@router.get("/cart/{cart_id}", response_model=list[Message])
def get_cart_messages(
    cart_id: int = Path(gt=0),
    limit: int = Query(default=50, ge=1, le=100),
    session: AuthSession = Depends(get_auth_session),
):
    return service.get_cart_messages(session, cart_id, limit)


@router.post("/cart/{cart_id}", response_model=Message, status_code=201)
def create_cart_message(
    body: MessageCreate,
    cart_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    return service.create_cart_message(session, cart_id, body)


@router.patch("/{message_id}", response_model=Message)
def update_message(
    body: MessageUpdate,
    message_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    return service.update_message(session, message_id, body)


@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    service.delete_message(session, message_id)
    return Response(status_code=204)
