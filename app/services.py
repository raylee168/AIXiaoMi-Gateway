from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import (
    BATCH_COMPLETED,
    BATCH_CREATED,
    BATCH_UPLOADING,
    CLEANUP_PENDING,
    EVENT_PENDING,
    EVENT_PHOTO_UPLOADED,
    PREPROCESS_PENDING,
    SOURCE_SERVER,
)
from app.core.config import get_settings
from app.models import PhotoFile, PluginEvent, UploadBatch
from app.schemas import UploadBatchCreate


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:24]}"


def _safe_ext(filename: str, mime_type: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    if mime_type == "image/png":
        return ".png"
    if mime_type == "image/webp":
        return ".webp"
    return ".jpg"


def create_batch(db: Session, payload: UploadBatchCreate) -> UploadBatch:
    batch = UploadBatch(
        upload_batch_id=_id("batch"),
        user_id=payload.user_id,
        source_channel=payload.source_channel,
        upload_type=payload.upload_type,
        photo_count=0,
        status=BATCH_CREATED,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def _batch_or_404(db: Session, upload_batch_id: str) -> UploadBatch:
    batch = db.scalar(select(UploadBatch).where(UploadBatch.upload_batch_id == upload_batch_id))
    if not batch:
        raise HTTPException(status_code=404, detail="upload_batch_not_found")
    return batch


def _make_dirs(user_id: str, upload_batch_id: str) -> tuple[Path, Path, Path]:
    root = Path(get_settings().storage_root)
    base = root / "uploads" / user_id / upload_batch_id
    original = base / "original"
    compressed = base / "compressed"
    thumbnails = base / "thumbnails"
    for path in (original, compressed, thumbnails):
        path.mkdir(parents=True, exist_ok=True)
    return original, compressed, thumbnails


def _save_variants(file: UploadFile, user_id: str, upload_batch_id: str, photo_id: str) -> tuple[str, str, str, int, int, int]:
    settings = get_settings()
    ext = _safe_ext(file.filename or "", file.content_type)
    original_dir, compressed_dir, thumbnail_dir = _make_dirs(user_id, upload_batch_id)
    original_path = original_dir / f"{photo_id}{ext}"
    compressed_path = compressed_dir / f"{photo_id}.jpg"
    thumbnail_path = thumbnail_dir / f"{photo_id}.jpg"
    raw = file.file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="empty_file")
    original_path.write_bytes(raw)
    try:
        with Image.open(original_path) as img:
            width, height = img.size
            rgb = img.convert("RGB")
            compressed = rgb.copy()
            compressed.thumbnail((settings.compressed_max_side, settings.compressed_max_side))
            compressed.save(compressed_path, format="JPEG", quality=86, optimize=True)
            thumb = rgb.copy()
            thumb.thumbnail((settings.thumbnail_max_side, settings.thumbnail_max_side))
            thumb.save(thumbnail_path, format="JPEG", quality=82, optimize=True)
    except UnidentifiedImageError as exc:
        original_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="invalid_image_file") from exc
    return (
        str(original_path),
        str(compressed_path),
        str(thumbnail_path),
        original_path.stat().st_size,
        width,
        height,
    )


def upload_photo(db: Session, upload_batch_id: str, user_id: str, file: UploadFile) -> PhotoFile:
    batch = _batch_or_404(db, upload_batch_id)
    if batch.user_id != user_id:
        raise HTTPException(status_code=400, detail="user_id_not_match_batch")
    if batch.status == BATCH_COMPLETED:
        raise HTTPException(status_code=400, detail="upload_batch_already_completed")
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="file_must_be_image")
    photo_id = _id("photo")
    original_path, compressed_path, thumbnail_path, file_size, width, height = _save_variants(
        file, user_id, upload_batch_id, photo_id
    )
    now = datetime.utcnow()
    row = PhotoFile(
        photo_id=photo_id,
        user_id=user_id,
        upload_batch_id=upload_batch_id,
        original_path=original_path,
        compressed_path=compressed_path,
        thumbnail_path=thumbnail_path,
        original_filename=file.filename or photo_id,
        mime_type=file.content_type or "image/jpeg",
        file_size=file_size,
        width=width,
        height=height,
        uploaded_at=now,
        expire_at=now + timedelta(hours=get_settings().file_expire_hours),
        preprocess_status=PREPROCESS_PENDING,
        cleanup_status=CLEANUP_PENDING,
    )
    batch.status = BATCH_UPLOADING
    batch.photo_count += 1
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def complete_batch(db: Session, upload_batch_id: str) -> PluginEvent:
    batch = _batch_or_404(db, upload_batch_id)
    photos = list(db.scalars(select(PhotoFile).where(PhotoFile.upload_batch_id == upload_batch_id)))
    if not photos:
        raise HTTPException(status_code=400, detail="upload_batch_has_no_photos")
    event_id = f"evt_{upload_batch_id}"
    existing = db.scalar(select(PluginEvent).where(PluginEvent.event_id == event_id))
    if existing:
        return existing
    now = datetime.utcnow()
    batch.status = BATCH_COMPLETED
    batch.completed_at = now
    event = PluginEvent(
        event_id=event_id,
        event_type=EVENT_PHOTO_UPLOADED,
        user_id=batch.user_id,
        source_server=SOURCE_SERVER,
        payload_json={
            "upload_batch_id": upload_batch_id,
            "photo_ids": [photo.photo_id for photo in photos],
            "uploaded_at": now.isoformat(),
        },
        status=EVENT_PENDING,
        retry_count=0,
        max_retry=3,
        next_run_at=now,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
