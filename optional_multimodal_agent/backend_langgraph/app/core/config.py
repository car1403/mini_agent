from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_mode: str = os.getenv("APP_MODE", "real")
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    storage_mode: str = os.getenv("STORAGE_MODE", "postgres")
    llm_fallback_enabled: bool = os.getenv("LLM_FALLBACK_ENABLED", "false").lower() == "true"
    llm_fallback_provider: str = os.getenv("LLM_FALLBACK_PROVIDER", "openai")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_vision_model: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-mini")
    openai_tts_model: str = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    openai_tts_voice: str = os.getenv("OPENAI_TTS_VOICE", "coral")
    max_image_size_mb: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "5"))
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://agent_user:agent_password@127.0.0.1:5433/agent_db",
    )
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    tools_mcp_url: str = os.getenv("TOOLS_MCP_URL", "http://127.0.0.1:8020/mcp")


settings = Settings()

if settings.app_mode != "real":
    raise RuntimeError("APP_MODE는 real만 지원합니다.")
if settings.storage_mode != "postgres":
    raise RuntimeError("STORAGE_MODE는 postgres만 지원합니다.")
if settings.llm_provider not in {"openai", "gemini", "ollama"}:
    raise RuntimeError("LLM_PROVIDER는 openai, gemini, ollama 중 하나여야 합니다.")
