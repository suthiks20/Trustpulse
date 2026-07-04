from datetime import datetime, timezone
from functools import lru_cache

from supabase import Client, create_client

from app.config import get_settings

settings = get_settings()


@lru_cache
def get_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def upload_photo(card_id: str, image_bytes: bytes) -> str:
    """Uploads to the private SUPABASE_BUCKET_NAME bucket and returns the storage key
    (not a URL — the bucket is private, so callers must go through get_signed_url)."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    storage_key = f"{card_id}/{timestamp}.jpg"

    get_client().storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
        storage_key, image_bytes, {"content-type": "image/jpeg"}
    )
    return storage_key


def get_signed_url(storage_key: str, expires_in: int = 300) -> str:
    result = get_client().storage.from_(settings.SUPABASE_BUCKET_NAME).create_signed_url(storage_key, expires_in)
    return result["signedURL"]
