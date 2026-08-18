"""Mini Agent 02의 동일한 TravelPlan Schema 결과를 Provider별로 비교합니다."""

import os

import httpx
from dotenv import load_dotenv


load_dotenv()
BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")


if __name__ == "__main__":
    try:
        response = httpx.post(
            f"{BASE_URL}/api/structured/compare",
            json={"providers": ["mock", "gemini", "openai", "ollama"], "message": "부산 대중교통 2박 3일 여행을 제안해 주세요."},
            timeout=90,
        )
        response.raise_for_status()
        for item in response.json()["results"]:
            print(f"\n[{item['provider']}] {item['status']}")
            print(item["content"] if item["status"] == "success" else item["error"])
    except httpx.HTTPError as error:
        print("Mini Agent 02 Backend 호출 실패:", error)
