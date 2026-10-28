from pydantic import BaseModel, ConfigDict, Field


class UserUpdate(BaseModel):
    """Only fields an authenticated user may update."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    location: str | None = Field(default=None, max_length=100)


class UserPublic(BaseModel):
    """Fields deliberately exposed by the public profile API."""

    userid: int
    name: str | None = None
    location: str | None = None
