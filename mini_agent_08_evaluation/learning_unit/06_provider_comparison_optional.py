"""선택 실습: 같은 요청을 설정된 Provider에 실행해 결과를 비교합니다."""

import json
import os

import httpx
from dotenv import load_dotenv


load_dotenv()
BASE_URL = os.getenv("PYTHON_AGENT_API_URL", "http://127.0.0.1:8000")
MESSAGE = "부산의 대표 장소를 포함한 2박 3일 여행을 제안해 주세요."


def run_provider(provider: str) -> dict:
    try:
        response = httpx.post(
            f"{BASE_URL}/api/providers/travel-plan",
            json={"provider": provider, "message": MESSAGE},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()["data"]
        return {
            "provider": provider,
            "status": "completed",
            "model": data["model"],
            "latency_ms": data["latency_ms"],
            "structured": isinstance(data["content"], dict),
        }
    except Exception as error:
        return {"provider": provider, "status": "failed", "error": str(error)}


if __name__ == "__main__":
    print("선택 실습: 설정된 Provider는 실제 비용과 시간이 발생할 수 있습니다.")
    report = [run_provider(name) for name in ("openai", "gemini", "ollama")]
    print(json.dumps(report, ensure_ascii=False, indent=2))
