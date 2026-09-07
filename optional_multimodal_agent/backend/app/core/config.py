"""Backend가 사용하는 환경변수를 읽습니다."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


REDIS_URL = env("REDIS_URL", "redis://127.0.0.1:6379/0")
MCP_URL = env("MCP_URL", "http://127.0.0.1:8020/mcp")
TTL = int(env("RUN_TTL_SECONDS", "86400"))
RUN_TIMEOUT = int(env("RUN_TIMEOUT_SECONDS", "600"))
MAX_TOOLS = int(env("MAX_TOOL_CALLS", "12"))
MAX_BYTES = int(env("MAX_UPLOAD_MB", "10")) * 1024 * 1024


def openai_client():
    from openai import AsyncOpenAI

    key = env("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY를 .env에 설정하세요.")
    return AsyncOpenAI(api_key=key, timeout=90, max_retries=1)
