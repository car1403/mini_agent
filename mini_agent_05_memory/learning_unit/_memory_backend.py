"""07~13 Memory 예제가 공유하는 Mini Agent 05 API Client입니다."""

import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")
PROVIDER = os.getenv("MEMORY_EXAMPLE_PROVIDER", os.getenv("LLM_PROVIDER", "openai"))
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))


def request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    response = httpx.request(
        method,
        f"{BASE_URL}{path}",
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def print_help(error: httpx.HTTPError) -> None:
    print("\n[실행 실패]")
    if isinstance(error, httpx.ConnectError):
        print(f"Backend에 연결할 수 없습니다: {BASE_URL}")
        print("Mini Agent 05 Backend가 실행 중인지 확인하세요.")
    elif isinstance(error, httpx.TimeoutException):
        print(f"Backend 응답 시간이 {REQUEST_TIMEOUT_SECONDS:g}초를 초과했습니다.")
        print("Redis·PostgreSQL·LLM 상태와 REQUEST_TIMEOUT_SECONDS를 확인하세요.")
    elif isinstance(error, httpx.HTTPStatusError):
        response = error.response
        print(f"Backend가 HTTP {response.status_code} 오류를 반환했습니다.")
        print("응답:", response.text)
        if response.status_code == 409:
            print("Session version 충돌이라면 최신 상태를 다시 조회한 후 재시도하세요.")
        elif response.status_code == 422:
            print("요청 값 또는 저장 가능한 Memory key인지 확인하세요.")
        elif response.status_code >= 500:
            print("Backend Terminal에서 Redis·PostgreSQL·LLM 연결 오류를 확인하세요.")
    else:
        print("HTTP 요청 실패:", error)

    print("환경 점검: python .\00_check_environment.py")
