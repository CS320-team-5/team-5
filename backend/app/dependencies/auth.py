from dataclasses import dataclass

from fastapi import Header, HTTPException
from postgrest.exceptions import APIError
from supabase import Client
from supabase_auth.errors import AuthApiError

from ..database import get_supabase, get_user_supabase


@dataclass(frozen=True)
class AuthSession:
    db: Client
    user_id: int
    auth_id: str
    access_token: str


def get_auth_session(
    authorization: str | None = Header(default=None),
) -> AuthSession:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header",
        )

    try:
        auth_response = get_supabase().auth.get_user(token)
    except AuthApiError as error:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
        ) from error

    user = auth_response.user

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user not found",
        )

    auth_id = str(user.id)

    db = get_user_supabase(token)

    try:
        rows = (
            db.table("users")
            .select("userid")
            .eq("authid", auth_id)
            .limit(1)
            .execute()
            .data
        )
    except APIError as error:
        raise HTTPException(
            status_code=503,
            detail="Could not resolve CoCart user profile",
        ) from error

    if not rows:
        raise HTTPException(
            status_code=403,
            detail="Authenticated account has no CoCart user profile",
        )

    return AuthSession(
        db=db,
        user_id=rows[0]["userid"],
        auth_id=auth_id,
        access_token=token,
    )