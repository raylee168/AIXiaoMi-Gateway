from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "aixiaomi-gateway"
    database_url: str = "mysql+pymysql://root@127.0.0.1:3306/core_album_db?charset=utf8mb4"
    storage_root: str = "/data/smart-album"
    file_expire_hours: int = 3
    compressed_max_side: int = 1600
    thumbnail_max_side: int = 320

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
