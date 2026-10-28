from fastapi import APIRouter, Depends, Path, Response
from supabase import Client

from ..dependencies.auth import AuthSession, get_auth_session
from ..database import get_supabase
from ..models.store import Store, StoreCreate, StoreUpdate
from ..services import store_service as service


router = APIRouter(prefix="/api/store", tags=["Store"])


# POST /api/store
@router.post("", response_model=Store, status_code=201)
def create_store(
    body: StoreCreate,
    session: AuthSession = Depends(get_auth_session),
):
    return service.create_store(session.db, body)


# GET /api/store/{store_id}
@router.get("/{store_id}", response_model=Store)
def get_store(
    store_id: int = Path(gt=0),
    db: Client = Depends(get_supabase),
):
    return service.get_store(db, store_id)


# GET /api/store
@router.get("", response_model=list[Store])
def get_all_stores(
    storetype: str | None = None,
    db: Client = Depends(get_supabase),
):
    return service.get_all_stores(db, storetype)


# PATCH /api/store/{store_id}
@router.patch("/{store_id}", response_model=Store)
def update_store(
    body: StoreUpdate,
    store_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    return service.update_store(session.db, store_id, body)


# DELETE /api/store/{store_id}
@router.delete("/{store_id}", status_code=204)
def delete_store(
    store_id: int = Path(gt=0),
    session: AuthSession = Depends(get_auth_session),
):
    service.delete_store(session.db, store_id)
    return Response(status_code=204)