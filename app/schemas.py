from pydantic import BaseModel, Field


class UploadBatchCreate(BaseModel):
    user_id: str
    source_channel: str = "app"
    upload_type: str = "manual"
    expected_photo_count: int | None = Field(default=None, ge=1)


class UploadBatchResponse(BaseModel):
    upload_batch_id: str
    status: str


class PhotoUploadResponse(BaseModel):
    photo_id: str
    original_path: str
    thumbnail_path: str
    preprocess_status: str


class UploadBatchCompleteResponse(BaseModel):
    upload_batch_id: str
    status: str
    event_id: str
