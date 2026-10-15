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
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Set SUPABASE_URL and SUPABASE_KEY in backend/.env"
        )

    return create_client(url, key)