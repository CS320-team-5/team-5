from pydantic import BaseModel, ConfigDict, Field


class PaymentHandles(BaseModel):
    venmo_handle: str | None = Field(default=None, min_length=1, max_length=100)
    zelle_identifier: str | None = Field(default=None, min_length=1, max_length=255)
    cash_app_handle: str | None = Field(default=None, min_length=1, max_length=100)


class PaymentHandlesUpdate(PaymentHandles):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)