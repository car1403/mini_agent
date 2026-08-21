"""환경 변수를 읽어 Backend 전체의 실행 설정을 제공합니다.

Router, Provider, Service와 Tool은 `settings`를 import해 모델·외부 API·제한값을 조회합니다.
"""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_vision_model: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-mini")
    openai_tts_model: str = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    openai_tts_voice: str = os.getenv("OPENAI_TTS_VOICE", "coral")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))
    weather_mode: str = os.getenv("WEATHER_MODE", "mock")
    open_meteo_base_url: str = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com").rstrip("/")
    open_meteo_geocoding_url: str = os.getenv("OPEN_METEO_GEOCODING_URL", "https://geocoding-api.open-meteo.com").rstrip("/")
    max_image_size_mb: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))


settings = Settings()
