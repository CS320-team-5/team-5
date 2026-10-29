from fastapi import APIRouter, Depends, Path, Response

from ..dependencies.auth import AuthSession, get_auth_session
from ..models.cartparticipant import CartParticipant
from ..services import cartparticipant as participant_service
from ..models.cartparticipant import CartParticipant, ParticipantJoin, ParticipantUpdate

router = APIRouter(
    prefix="/api/cart",
    tags=["Cart Participants"],
)


@router.get(
    "/{cart_id}/participants",
    response_model=list[CartParticipant],
)
def get_active_participants(
    cart_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    return participant_service.get_active_participants(
        cart_id=cart_id,
        session=session,
    )

@router.post(
    "/{cart_id}/participants",
    response_model=CartParticipant,
    status_code=201,
)
def join_cart(
    body: ParticipantJoin,
    cart_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    return participant_service.join_cart(
        cart_id=cart_id,
        body=body,
        session=session,
    )

@router.patch(
    "/{cart_id}/participants/me",
    response_model=CartParticipant,
)
def update_contribution(
    body: ParticipantUpdate,
    cart_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    return participant_service.update_contribution(
        cart_id=cart_id,
        body=body,
        session=session,
    )

@router.delete(
    "/{cart_id}/participants/me",
    status_code=204,
)
def leave_cart(
    cart_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    participant_service.leave_cart(
        cart_id=cart_id,
        session=session,
    )

    return Response(status_code=204)