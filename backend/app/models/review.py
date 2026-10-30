
from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    targetuserid: int = Field(gt=0)
    authoruserid: int = Field(gt=0)
    rating: int
    commentbody: str | None = None


class ReviewUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rating: int | None = None
    commentbody: str | None = None


class ReviewResponse(BaseModel):
    reviewid: int
    targetuserid: int
    authoruserid: int
    rating: int
    commentbody: str | None = None
