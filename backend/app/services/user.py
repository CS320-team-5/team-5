from typing import NoReturn

from fastapi import HTTPException
from httpx import RequestError
from postgrest.exceptions import APIError
from supabase import Client

from ..dependencies.auth import AuthSession
from ..models.user import UserPublic, UserUpdate
from ..repositories import user as user_repository


def _raise_database_error(error: APIError | RequestError) -> NoReturn:
    """Translate known Supabase failures into existing API error responses."""

    if isinstance(error, RequestError):
        raise HTTPException(
            status_code=503,
            detail="Could not reach Supabase",
        ) from error

    if error.code == "23505":
        raise HTTPException(
            status_code=409,
            detail="A user with this unique value already exists",
        ) from error

    if error.code in {"42501", "PGRST301", "PGRST302"}:
        raise HTTPException(
            status_code=403,
            detail="Database access denied",
        ) from error

    if error.code in {"23502", "23514", "22003"}:
        raise HTTPException(
            status_code=422,
            detail="Database constraint failed",
        ) from error

    raise HTTPException(
        status_code=503,
        detail="Supabase could not complete the request",
    ) from error


def get_user_profile(db: Client, user_id: int) -> UserPublic:
    """Read a public profile, returning 404 if it does not exist."""

    try:
        row = user_repository.find_user(db, user_id)
    except (APIError, RequestError) as error:
        _raise_database_error(error)

    if row is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPublic.model_validate(row)


def update_current_user_profile(
    session: AuthSession,
    body: UserUpdate,
) -> UserPublic:
    """Only the signed-in user may change their own allowed profile fields."""

    changes = body.model_dump(exclude_unset=True)

    if not changes:
        return get_user_profile(session.db, session.user_id)

    try:
        row = user_repository.update_user(session.db, session.user_id, changes)
    except (APIError, RequestError) as error:
        _raise_database_error(error)

    if row is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPublic.model_validate(row)
