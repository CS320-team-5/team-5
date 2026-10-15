from decimal import Decimal
from itertools import count
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Response
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

CartStatus = Literal["Active", "Inactive"]

class CartCreate(BaseModel):
    """JSON fields the frontend sends when creating a cart."""
    model_config = ConfigDict(extra="forbid")
    storeid: int = Field(gt=0)
    location: str | None = Field(default=None, max_length=30)
    deadline: AwareDatetime | None = None
    minimumamount: Decimal = Field(ge=0, max_digits=10, decimal_places=2)


class CartUpdate(BaseModel):
    """Omit fields to keep them; location and deadline may be cleared with null."""
    model_config = ConfigDict(extra="forbid")
    location: str | None = Field(default=None, max_length=30)
    deadline: AwareDatetime | None = None
    status: CartStatus | None = None
    minimumamount: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)


class Cart(CartCreate):
    """The full cart returned to the frontend."""
    cartid: int
    owneruserid: int
    status: CartStatus = "Active"
    currentamount: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)


# MOCK DATABASE: replace reads/writes here with the team's database calls.
carts: dict[int, Cart] = {}
# MOCK IDs: 1, 2, 3 ... . The supplied SQL does not generate IDs yet.
# TODO: Agree on database ID generation before replacing this counter.
cart_ids = count(1)


def get_current_user_id() -> int:
    return 1


def find_cart(cart_id: int) -> Cart:
    if cart_id not in carts:
        raise HTTPException(status_code=404, detail="Cart not found")
    return carts[cart_id]


def check_owner(cart: Cart, user_id: int) -> None:
    if cart.owneruserid != user_id:
        raise HTTPException(status_code=403, detail="Only the owner can change this cart")


router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.post("", response_model=Cart, status_code=201)
def create_cart(body: CartCreate, user_id: int = Depends(get_current_user_id)):
    cart = Cart(**body.model_dump(), cartid=next(cart_ids), owneruserid=user_id)
    carts[cart.cartid] = cart
    return cart

@router.get("", response_model=list[Cart])
def get_all_carts(
    status: CartStatus | None = None,
    storeid: int | None = None,
    owneruserid: int | None = None,
):
    results = list(carts.values())
    if status is not None:
        results = [cart for cart in results if cart.status == status]
    if storeid is not None:
        results = [cart for cart in results if cart.storeid == storeid]
    if owneruserid is not None:
        results = [cart for cart in results if cart.owneruserid == owneruserid]
    return results

@router.get("/{cart_id}", response_model=Cart)
def get_cart(cart_id: int = Path(gt=0)):
    return find_cart(cart_id)

@router.patch("/{cart_id}", response_model=Cart)
def update_cart(
    body: CartUpdate,
    cart_id: int = Path(gt=0),
    user_id: int = Depends(get_current_user_id),
):
    cart = find_cart(cart_id)
    check_owner(cart, user_id)
    changes = body.model_dump(exclude_unset=True)
    if any(changes.get(field) is None for field in ("status", "minimumamount") if field in changes):
        raise HTTPException(status_code=422, detail="status and minimumamount cannot be null")
        
    updated_cart = Cart(**{**cart.model_dump(), **changes})
    carts[cart_id] = updated_cart
    return updated_cart


@router.delete("/{cart_id}", status_code=204)
def delete_cart(cart_id: int = Path(gt=0), user_id: int = Depends(get_current_user_id)):
    cart = find_cart(cart_id)
    check_owner(cart, user_id)
    del carts[cart_id]
    return Response(status_code=204)


