from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart Medical Store IR System"
    env: str = "development"
    database_url: str = "sqlite:///./data/medical_store.db"
    data_json_path: str = "./data/medicines.json"
    data_csv_path: str = "./data/medicines.csv"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    bm25_weight: float = 0.55
    semantic_weight: float = 0.45
    max_results: int = 20
    cache_size: int = 2048
    rate_limit_per_minute: int = 120

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
