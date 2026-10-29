from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

ParticipantStatus = Literal["Active", "Inactive"]

#The amount the signed-in user plans to contribute.
class ParticipantJoin(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amountcontributed: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=10,
        decimal_places=2,
    )


#The user's new contribution amount.
class ParticipantUpdate(BaseModel): 
    model_config = ConfigDict(extra="forbid")
    amountcontributed: Decimal = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
    )

#A participant record returned by the API.
class CartParticipant(BaseModel):
    cartid: int
    userid: int
    status: ParticipantStatus
    amountcontributed: Decimal = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
    )
    joindate: date