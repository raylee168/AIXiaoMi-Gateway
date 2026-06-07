import io
import os
import tempfile
from pathlib import Path

db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
storage_root = tempfile.mkdtemp(prefix="smart_album_upload_")
os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"
os.environ["STORAGE_ROOT"] = storage_root

from fastapi.testclient import TestClient
from PIL import Image

from app.db.base import Base
from app.db.session import engine
from app.main import app


Base.metadata.create_all(bind=engine)
client = TestClient(app)


def _image_bytes(color: tuple[int, int, int]) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (800, 600), color).save(buf, format="JPEG")
    return buf.getvalue()


def test_upload_batch_photos_and_plugin_event():
    batch = client.post(
        "/api/upload/batches",
        json={"user_id": "u_upload", "source_channel": "app", "upload_type": "manual", "expected_photo_count": 2},
    ).json()
    upload_batch_id = batch["upload_batch_id"]

    photo_ids = []
    for color in [(255, 0, 0), (0, 255, 0)]:
        response = client.post(
            f"/api/upload/batches/{upload_batch_id}/photos",
            data={"user_id": "u_upload"},
            files={"file": ("photo.jpg", _image_bytes(color), "image/jpeg")},
        )
        assert response.status_code == 200
        payload = response.json()
        photo_ids.append(payload["photo_id"])
        assert Path(payload["original_path"]).exists()
        assert Path(payload["thumbnail_path"]).exists()
        assert payload["preprocess_status"] == "pending"

    complete = client.post(f"/api/upload/batches/{upload_batch_id}/complete")
    assert complete.status_code == 200
    event = complete.json()
    assert event["status"] == "completed"
    assert event["event_id"] == f"evt_{upload_batch_id}"

    duplicate = client.post(f"/api/upload/batches/{upload_batch_id}/complete")
    assert duplicate.status_code == 200
    assert duplicate.json()["event_id"] == event["event_id"]
