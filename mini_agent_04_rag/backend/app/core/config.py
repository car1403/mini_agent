from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    ollama_embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "embeddinggemma")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://agent_user:agent_password@127.0.0.1:5433/agent_db",
    )
    rag_collection: str = os.getenv("RAG_COLLECTION", "mini_agent_travel")
    rag_min_score: float = float(os.getenv("RAG_MIN_SCORE", "0.35"))
    redis_url: str = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    rag_cache_ttl_seconds: int = int(os.getenv("RAG_CACHE_TTL_SECONDS", "300"))
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))
    max_pdf_size_mb: int = int(os.getenv("MAX_PDF_SIZE_MB", "20"))


settings = Settings()
