from decimal import Decimal
from typing import Literal
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field




CartStatus = Literal["Active", "Inactive"]


class CartBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    storeid: int = Field(gt=0)
    location: str | None = Field(default=None, max_length=30)
    deadline: AwareDatetime
    notes: str | None = Field(default=None, max_length=500)
    minimumamount: Decimal = Field(
        gt=0, max_digits=10, decimal_places=2
    )

class CartCreate(CartBase):
    owneramount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=10,
        decimal_places=2,
    )

class CartUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    notes: str | None = Field(default=None, max_length=500)
    location: str | None = Field(default=None, max_length=30)
    deadline: AwareDatetime | None = None
    status: CartStatus | None = None
    minimumamount: Decimal | None = Field(default=None,gt=0,max_digits=10,decimal_places=2,)

class Cart(CartBase):
    cartid: int
    owneruserid: int
    status: CartStatus = "Active"
    currentamount: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2,)