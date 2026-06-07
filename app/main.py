from fastapi import Depends, FastAPI, File, Form, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import (
    PhotoUploadResponse,
    UploadBatchCompleteResponse,
    UploadBatchCreate,
    UploadBatchResponse,
)
from app.services import complete_batch, create_batch, upload_photo

app = FastAPI(title="AIXiaoMi Gateway Photo Upload Server", version="0.1.0")


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "service": "aixiaomi-gateway"}


@app.post("/api/upload/batches", response_model=UploadBatchResponse)
def post_upload_batch(payload: UploadBatchCreate, db: Session = Depends(get_db)):
    batch = create_batch(db, payload)
    return {"upload_batch_id": batch.upload_batch_id, "status": batch.status}


@app.post("/api/upload/batches/{upload_batch_id}/photos", response_model=PhotoUploadResponse)
def post_photo(
    upload_batch_id: str,
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    photo = upload_photo(db, upload_batch_id, user_id, file)
    return {
        "photo_id": photo.photo_id,
        "original_path": photo.original_path,
        "thumbnail_path": photo.thumbnail_path,
        "preprocess_status": photo.preprocess_status,
    }


@app.post("/api/upload/batches/{upload_batch_id}/complete", response_model=UploadBatchCompleteResponse)
def post_batch_complete(upload_batch_id: str, db: Session = Depends(get_db)):
    event = complete_batch(db, upload_batch_id)
    return {
        "upload_batch_id": upload_batch_id,
        "status": "completed",
        "event_id": event.event_id,
    }
