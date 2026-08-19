"""Prompt 실험 예제가 공통으로 사용하는 Mini Agent 02 API Client입니다."""

import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()
BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")
PROVIDER = os.getenv("PROMPT_EXAMPLE_PROVIDER", "mock")


def generate_text(system_prompt: str, message: str) -> dict[str, Any]:
    response = httpx.post(
        f"{BASE_URL}/api/generate",
        json={"provider": PROVIDER, "system_prompt": system_prompt, "message": message},
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


def generate_structured(schema_type: str, system_prompt: str, message: str) -> dict[str, Any]:
    response = httpx.post(
        f"{BASE_URL}/api/structured/generate",
        json={"provider": PROVIDER, "schema_type": schema_type, "system_prompt": system_prompt, "message": message},
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


def print_result(label: str, result: dict[str, Any]) -> None:
    print(f"\n===== {label} =====")
    print(f"{result['provider']} · {result['model']} · {result['latency_ms']}ms")
    print(result["content"])


def print_connection_help(error: httpx.HTTPError) -> None:
    print("Mini Agent 02 Backend 호출 실패:", error)
    print("Backend와 BACKEND_API_URL을 확인하세요.")
