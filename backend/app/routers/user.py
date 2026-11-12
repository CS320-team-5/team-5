from fastapi import APIRouter, Depends, Path, HTTPException, Response
from supabase import Client

from ..database import get_supabase, get_supabase_admin
from ..dependencies.auth import AuthSession, get_auth_session
from ..models.user import UserPublic, UserUpdate
from ..services import user as user_service
from ..models.settings import UserSettings
from ..repositories.settings import get_user_settings
from ..models.settings import UserSettings, UserSettingsUpdate
from ..repositories.settings import get_user_settings, update_user_settings
from httpx import RequestError
from postgrest.exceptions import APIError
from supabase_auth.errors import AuthApiError

router = APIRouter(prefix="/api/user", tags=["User"])


@router.get("/me", response_model=UserPublic)
def get_current_user(
    session: AuthSession = Depends(get_auth_session),
):
    return user_service.get_user(session.db, session.user_id)


@router.patch("/me", response_model=UserPublic)
def update_current_user(
    body: UserUpdate,
    session: AuthSession = Depends(get_auth_session),
):
    return user_service.update_user(session.db, session.user_id, body)

@router.get("/me/settings", response_model=UserSettings)
def get_current_user_settings(
    session: AuthSession = Depends(get_auth_session),
):
    try:
        return get_user_settings(session.db, session.auth_id)
    except (APIError, RequestError) as error:
        raise HTTPException(
            status_code=503, detail="Could not load settings"
        ) from error

@router.patch("/me/settings", response_model=UserSettings)
def update_current_user_settings(
    body: UserSettingsUpdate,
    session: AuthSession = Depends(get_auth_session),
):
    changes = body.model_dump(exclude_unset=True)
    try:
        return update_user_settings(session.db, session.auth_id, changes)
    except (APIError, RequestError) as error:
        raise HTTPException(
            status_code=503, detail="Could not save settings"
        ) from error

@router.delete("/me", status_code=204)
def delete_current_user(
    session: AuthSession = Depends(get_auth_session),
) -> Response:
    try:
        admin = get_supabase_admin()
        admin.auth.admin.delete_user(session.auth_id, should_soft_delete=False)
    except (AuthApiError, RequestError, RuntimeError) as error:
        print(
            "Account deletion failed:",
            type(error).__name__,
            "status:", getattr(error, "status", None),
            "code:", getattr(error, "code", None),
        )
        raise HTTPException(
            status_code=503, detail="Could not delete account"
        ) from error

    return Response(status_code=204)

@router.get("/{user_id}", response_model=UserPublic)
def get_user(
    user_id: int = Path(gt=0),
    db: Client = Depends(get_supabase),
):
    return user_service.get_public_user(db, user_id)