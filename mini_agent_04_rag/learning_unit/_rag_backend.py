"""실제 RAG 예제가 공유하는 Mini Agent 04 API Client입니다."""

import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")
PROVIDER = os.getenv("RAG_EXAMPLE_PROVIDER", "mock")


def request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    # 실제 저장소와 LLM은 Mini Agent Backend를 통해 동일한 계약으로 호출합니다.
    response = httpx.request(method, f"{BASE_URL}{path}", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def print_help(error: httpx.HTTPError) -> None:
    print("Mini Agent 04 Backend 호출 실패:", error)
    print("Ollama·PostgreSQL·Redis와 BACKEND_API_URL 설정을 확인하세요.")
