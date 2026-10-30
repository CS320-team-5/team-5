from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class StoreCreate(BaseModel):
    """Fields sent when creating a store."""
    model_config = ConfigDict(extra="forbid")

    enterprisename: str = Field(min_length=1)
    storetype: str = Field(min_length=1)
    address: str = Field(min_length=1)
    minimumorderamount: Decimal = Field(ge=0)


class StoreUpdate(BaseModel):
    """Only supplied fields are updated."""
    model_config = ConfigDict(extra="forbid")

    enterprisename: str | None = Field(default=None, min_length=1)
    storetype: str | None = Field(default=None, min_length=1)
    address: str | None = Field(default=None, min_length=1)
    minimumorderamount: Decimal | None = Field(
        default=None, ge=0
    )


class Store(StoreCreate):
    """Full store record returned to the frontend."""
    storeid: int = Field(gt=0)