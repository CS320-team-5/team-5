"""Models matching the existing public.message Supabase table."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MessageCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    messagetext: str = Field(min_length=1, max_length=2000)

    @field_validator("messagetext")
    @classmethod
    def nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message must not be blank")
        return value


class MessageUpdate(MessageCreate):
    pass


class Message(BaseModel):
    messageid: int
    cartid: int
    userid: int
    messagetext: str
    timestamp: datetime
