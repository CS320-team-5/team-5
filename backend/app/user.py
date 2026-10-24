from fastapi import APIRouter, Depends, HTTPException, Path
from httpx import RequestError
from postgrest.exceptions import APIError
from pydantic import BaseModel, ConfigDict, Field
from supabase import Client

from .auth import AuthSession, get_auth_session
from .database import get_supabase


router = APIRouter(
    prefix="/api/user",
    tags=["User"],
)


class UserUpdate(BaseModel):
    """
    Fields a user is allowed to change about their own profile.

    userid and authid are intentionally not included because those values
    should never be controlled by the frontend.
    """

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    location: str | None = Field(
        default=None,
        max_length=100,
    )


def execute_query(query):
    """
    Execute a Supabase query and convert database errors into API responses.
    """

    try:
        return query.execute().data

    except APIError as error:
        code = error.code

        if code == "23505":
            raise HTTPException(
                status_code=409,
                detail="A user with this unique value already exists",
            ) from error

        if code in {"42501", "PGRST301", "PGRST302"}:
            raise HTTPException(
                status_code=403,
                detail="Database access denied",
            ) from error

        if code in {"23502", "23514", "22003"}:
            raise HTTPException(
                status_code=422,
                detail="Database constraint failed",
            ) from error

        raise HTTPException(
            status_code=503,
            detail="Supabase could not complete the request",
        ) from error

    except RequestError as error:
        raise HTTPException(
            status_code=503,
            detail="Could not reach Supabase",
        ) from error


def remove_private_fields(user: dict) -> dict:
    """
    Remove internal authentication information before sending a user
    profile to the frontend.
    """

    public_user = dict(user)

    public_user.pop("authid", None)

    return public_user


def find_user(
    db: Client,
    user_id: int,
) -> dict:
    """
    Find a CoCart user by their integer userid.
    """

    rows = execute_query(
        db.table("users")
        .select("*")
        .eq("userid", user_id)
        .limit(1)
    )

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return rows[0]


@router.get("/me")
def get_current_user_profile(
    session: AuthSession = Depends(get_auth_session),
):
    """
    Return the profile belonging to the authenticated user.
    """

    user = find_user(
        session.db,
        session.user_id,
    )

    return remove_private_fields(user)


@router.patch("/me")
def update_current_user_profile(
    body: UserUpdate,
    session: AuthSession = Depends(get_auth_session),
):
    """
    Update the authenticated user's own profile.

    The userid comes from the verified JWT/session rather than from
    the request body.
    """

    changes = body.model_dump(
        exclude_unset=True,
    )

    if not changes:
        user = find_user(
            session.db,
            session.user_id,
        )

        return remove_private_fields(user)

    rows = execute_query(
        session.db
        .table("users")
        .update(changes)
        .eq("userid", session.user_id)
        .select("*")
    )

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return remove_private_fields(rows[0])


@router.get("/{user_id}")
def get_user(
    user_id: int = Path(gt=0),
    db: Client = Depends(get_supabase),
):
    """
    Return another user's public CoCart profile.
    """

    user = find_user(
        db,
        user_id,
    )

    return remove_private_fields(user)