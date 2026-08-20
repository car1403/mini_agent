"""Tool Use 실제 호출 예제가 공유하는 Mini Agent 03 API Client입니다."""

import os
from typing import Any

import httpx
from dotenv import load_dotenv


# .env와 환경 변수로 Backend 주소와 실험 Provider를 바꿀 수 있습니다.
load_dotenv()
BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")
PROVIDER = os.getenv("TOOL_EXAMPLE_PROVIDER", "mock")


def post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    # 모든 실제 호출 예제가 같은 HTTP 오류 처리와 timeout을 사용합니다.
    response = httpx.post(f"{BASE_URL}{path}", json=payload, timeout=90)
    response.raise_for_status()
    return response.json()


def select_tool(
    message: str,
    tool_choice: str = "auto",
) -> dict[str, Any]:
    # 이 API는 Tool Call을 제안할 뿐 Tool 함수를 실행하지 않습니다.
    return post("/api/tools/select", {
        "provider": PROVIDER,
        "message": message,
        "tool_choice": tool_choice,
    })


def complete_loop(
    message: str,
    tool_choice: str = "auto",
) -> dict[str, Any]:
    # complete API는 선택·검증·실행·최종 답변의 전체 Loop를 수행합니다.
    return post("/api/tools/complete", {
        "provider": PROVIDER,
        "message": message,
        "tool_choice": tool_choice,
    })


def print_result(label: str, result: dict[str, Any]) -> None:
    print(f"\n===== {label} =====")
    print(result)


def print_help(error: httpx.HTTPError) -> None:
    print("Mini Agent 03 Backend 호출 실패:", error)
    print("Backend와 BACKEND_API_URL을 확인하세요.")
    print("실제 비교는 TOOL_EXAMPLE_PROVIDER를 gemini, openai, ollama 중 하나로 설정하세요.")
