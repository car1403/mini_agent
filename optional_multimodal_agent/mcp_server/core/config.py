"""MCP Server가 사용하는 환경변수를 읽습니다."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


DATABASE_URL = env(
    "DATABASE_URL",
    "postgresql://agent_user:agent_password@127.0.0.1:5433/multimodal_agent_db",
)
MAX_BYTES = int(env("MAX_UPLOAD_MB", "10")) * 1024 * 1024


def openai_client():
    from openai import AsyncOpenAI

    key = env("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY를 .env에 설정하세요.")
    return AsyncOpenAI(api_key=key, timeout=90, max_retries=1)
