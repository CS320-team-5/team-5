from fastapi import APIRouter, Depends, Path, Response
from supabase import Client

from ..database import get_supabase
from ..dependencies.auth import AuthSession, get_auth_session
from ..models.cart import Cart, CartCreate, CartStatus, CartUpdate
from ..services import cart as cart_service


router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.post("", response_model=Cart, status_code=201)
def create_cart(
    body: CartCreate,
    session: AuthSession = Depends(get_auth_session),
):
    return cart_service.create_cart(body, session)

#gets the previous cart of a user that has a deadline that has passed and returns it in descending order of deadline

@router.get("/history", response_model=list[Cart])
def get_cart_history(
    session: AuthSession = Depends(get_auth_session),
):
    return cart_service.get_cart_history(session)

@router.get("/{cart_id}", response_model=Cart)
def get_cart(
    cart_id: int = Path(gt=0),
    db: Client = Depends(get_supabase),
):
    return cart_service.get_cart(db, cart_id)

@router.get("", response_model=list[Cart])
def get_all_carts(
    status: CartStatus | None = None,
    storeid: int | None = None,
    owneruserid: int | None = None,
    location: str | None = None,
    db: Client = Depends(get_supabase),
):
    return cart_service.get_all_carts(
        db=db,
        status=status,
        storeid=storeid,
        owneruserid=owneruserid,
        location=location,
    )

@router.patch("/{cart_id}", response_model=Cart)
def update_cart(
    body: CartUpdate,
    cart_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    return cart_service.update_cart(
        body=body,
        cart_id=cart_id,
        session=session,
    )


@router.delete("/{cart_id}", status_code=204)
def delete_cart(
    cart_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    cart_service.delete_cart(
        cart_id=cart_id,
        session=session,
    )

    return Response(status_code=204)