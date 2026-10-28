from fastapi import APIRouter, Depends, Path
from supabase import Client

from ..database import get_supabase
from ..dependencies.auth import AuthSession, get_auth_session
from ..models.user import UserPublic, UserUpdate
from ..services import user as user_service


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


@router.get("/{user_id}", response_model=UserPublic)
def get_user(
    user_id: int = Path(gt=0),
    db: Client = Depends(get_supabase),
):
    return user_service.get_user(db, user_id)