import os
import uuid
from typing import Optional
from core.supabase_client import get_client

STORAGE_BUCKET = "job-photos"


def upload_photo(
    file_bytes: bytes,
    filename: str,
    job_id: str,
    task_id: Optional[str] = None,
    notes: str = "",
) -> dict:
    """Upload photo to Supabase Storage and create DB record. Returns photo record."""
    db = get_client()

    # Build storage path: job_id/filename (unique)
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    storage_path = f"{job_id}/{unique_name}"

    # Upload to Supabase Storage
    db.storage.from_(STORAGE_BUCKET).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": _guess_mime(ext)},
    )

    # Get public URL
    url_response = db.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
    file_url = url_response

    # Store DB record
    payload = {
        "job_id": job_id,
        "task_id": task_id,
        "file_url": file_url,
        "filename": filename,
        "notes": notes,
    }
    result = db.table("photos").insert(payload).execute()
    return result.data[0]


def get_photos_for_job(job_id: str) -> list[dict]:
    db = get_client()
    result = (
        db.table("photos")
        .select("*")
        .eq("job_id", job_id)
        .order("uploaded_at", desc=True)
        .execute()
    )
    return result.data or []


def get_photos_for_task(task_id: str) -> list[dict]:
    db = get_client()
    result = (
        db.table("photos")
        .select("*")
        .eq("task_id", task_id)
        .order("uploaded_at", desc=True)
        .execute()
    )
    return result.data or []


def delete_photo(photo_id: str) -> None:
    db = get_client()
    db.table("photos").delete().eq("id", photo_id).execute()


def _guess_mime(ext: str) -> str:
    ext = ext.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".heic": "image/heic",
    }.get(ext, "application/octet-stream")
