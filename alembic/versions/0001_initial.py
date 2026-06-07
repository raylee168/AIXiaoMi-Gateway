"""initial gateway schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-07
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("upload_batches",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("upload_batch_id", sa.String(64), nullable=False, unique=True),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("source_channel", sa.String(32), nullable=False),
        sa.Column("upload_type", sa.String(32), nullable=False),
        sa.Column("photo_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_upload_batches_upload_batch_id", "upload_batches", ["upload_batch_id"])
    op.create_index("ix_upload_batches_user_id", "upload_batches", ["user_id"])
    op.create_index("ix_upload_batches_status", "upload_batches", ["status"])
    op.create_table("photo_files",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("photo_id", sa.String(64), nullable=False, unique=True),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("upload_batch_id", sa.String(64), nullable=False),
        sa.Column("original_path", sa.String(1024), nullable=False),
        sa.Column("compressed_path", sa.String(1024), nullable=False),
        sa.Column("thumbnail_path", sa.String(1024), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("renamed_filename", sa.String(255)),
        sa.Column("mime_type", sa.String(64), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.Column("expire_at", sa.DateTime(), nullable=False),
        sa.Column("preprocess_status", sa.String(32), nullable=False),
        sa.Column("smart_reject_count", sa.Integer(), nullable=False),
        sa.Column("smart_reject_status", sa.String(32), nullable=False),
        sa.Column("used_in_generation", sa.Integer(), nullable=False),
        sa.Column("cleanup_status", sa.String(32), nullable=False),
        sa.Column("cleaned_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_photo_files_photo_id", "photo_files", ["photo_id"])
    op.create_index("ix_photo_files_user_id", "photo_files", ["user_id"])
    op.create_index("ix_photo_files_upload_batch_id", "photo_files", ["upload_batch_id"])
    op.create_index("ix_photo_files_preprocess_status", "photo_files", ["preprocess_status"])
    op.create_index("ix_photo_files_cleanup_status", "photo_files", ["cleanup_status"])
    op.create_table("plugin_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("event_id", sa.String(64), nullable=False, unique=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("source_server", sa.String(64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("max_retry", sa.Integer(), nullable=False),
        sa.Column("locked_by", sa.String(128)),
        sa.Column("locked_until", sa.DateTime()),
        sa.Column("next_run_at", sa.DateTime(), nullable=False),
        sa.Column("processed_at", sa.DateTime()),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_plugin_events_event_id", "plugin_events", ["event_id"])
    op.create_index("ix_plugin_events_event_type", "plugin_events", ["event_type"])
    op.create_index("ix_plugin_events_user_id", "plugin_events", ["user_id"])
    op.create_index("ix_plugin_events_status", "plugin_events", ["status"])


def downgrade() -> None:
    op.drop_table("plugin_events")
    op.drop_table("photo_files")
    op.drop_table("upload_batches")
