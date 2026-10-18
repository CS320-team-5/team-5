import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client


# Find and load backend/.env.
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


@lru_cache
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in backend/.env"
        )

    return create_client(url, key)

def get_user_supabase(access_token: str) -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in backend/.env"
        )

    client = create_client(url, key)
    client.postgrest.auth(access_token)

    return client