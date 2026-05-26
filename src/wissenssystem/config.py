from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_url: str = "http://localhost:11434"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: SecretStr | None = None

    data_dir: Path = Path("data")
    sources_dir: Path = Path("data/sources")
    blobs_dir: Path = Path("data/blobs")
    registry_db_path: Path = Path("data/registry.db")

    # LLM provider: "ollama" or "anthropic"
    # Set USE_VISION_PARSER=false to force Docling for this ingest
    use_vision_parser: bool = True
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-6"
    vision_model: str = "moondream"
    embedding_model: str = "intfloat/multilingual-e5-large"

    anthropic_api_key: SecretStr | None = None

    intent_confidence_threshold: float = 0.7
    machine_resolution_threshold: float = 0.75
    retrieval_top_k: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
