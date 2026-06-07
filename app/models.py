from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

IdType = BigInteger().with_variant(Integer, "sqlite")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class UploadBatch(Base, TimestampMixin):
    __tablename__ = "upload_batches"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    upload_batch_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_channel: Mapped[str] = mapped_column(String(32), nullable=False)
    upload_type: Mapped[str] = mapped_column(String(32), nullable=False)
    photo_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="created", index=True, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)


class PhotoFile(Base, TimestampMixin):
    __tablename__ = "photo_files"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    photo_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    upload_batch_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    original_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    compressed_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    thumbnail_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    renamed_filename: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expire_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    preprocess_status: Mapped[str] = mapped_column(String(32), default="pending", index=True, nullable=False)
    smart_reject_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    smart_reject_status: Mapped[str] = mapped_column(String(32), default="none", nullable=False)
    used_in_generation: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cleanup_status: Mapped[str] = mapped_column(String(32), default="pending", index=True, nullable=False)
    cleaned_at: Mapped[datetime | None] = mapped_column(DateTime)


class PluginEvent(Base, TimestampMixin):
    __tablename__ = "plugin_events"

    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_server: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retry: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    locked_by: Mapped[str | None] = mapped_column(String(128))
    locked_until: Mapped[datetime | None] = mapped_column(DateTime)
    next_run_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)
