# AIXiaoMi Gateway

照片上传服务，负责创建上传批次、保存原图、生成压缩图和缩略图，并写入 `photo_files` 与 `plugin_events`。

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=mysql+pymysql://user:password@host:3306/core_album_db?charset=utf8mb4
set STORAGE_ROOT=/data/smart-album
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8002
```
