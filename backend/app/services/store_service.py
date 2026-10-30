from fastapi import HTTPException
from supabase import Client

from ..models.store import Store, StoreCreate, StoreUpdate
from ..repositories import store_repository as repository


def create_store(db: Client, body: StoreCreate) -> Store:
    values = body.model_dump(mode="json")
    rows = repository.create_store_record(db, values)

    if not rows:
        raise HTTPException(502, "Insert returned no store")

    return Store(**rows[0])


def get_store(db: Client, store_id: int) -> Store:
    return repository.find_store(db, store_id)


def get_all_stores(
    db: Client, storetype: str | None = None
) -> list[Store]:
    rows = repository.get_all_store_records(db, storetype)
    return [Store(**row) for row in rows]


def update_store(
    db: Client, store_id: int, body: StoreUpdate
) -> Store:
    # Confirm the store exists.
    existing_store = repository.find_store(db, store_id)

    changes = body.model_dump(
        mode="json",
        exclude_unset=True,
    )

    for field, value in changes.items():
        if value is None:
            raise HTTPException(422, f"{field} cannot be null")

    if not changes:
        return existing_store

    rows = repository.update_store_record(db, store_id, changes)

    if not rows:
        raise HTTPException(409, "No updated store returned")

    return Store(**rows[0])


def delete_store(db: Client, store_id: int) -> None:
    repository.find_store(db, store_id)

    rows = repository.delete_store_record(db, store_id)

    if not rows:
        raise HTTPException(409, "No deleted store returned")