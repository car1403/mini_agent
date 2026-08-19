"""Mini Agent 02의 TravelPlan·SupportTicket 결과를 Provider별로 비교합니다."""

import os

import httpx
from dotenv import load_dotenv


load_dotenv()
BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")
SAMPLES = {
    "travel_plan": "부산 대중교통 2박 3일 여행을 제안해 주세요.",
    "support_ticket": "결제가 두 번 된 것 같습니다. 주문 번호는 아직 찾지 못했습니다.",
}


if __name__ == "__main__":
    try:
        for schema_type, message in SAMPLES.items():
            print(f"\n===== {schema_type} =====")
            response = httpx.post(
                f"{BASE_URL}/api/structured/compare",
                json={"providers": ["mock", "gemini", "openai", "ollama"], "schema_type": schema_type, "message": message},
                timeout=90,
            )
            response.raise_for_status()
            for item in response.json()["results"]:
                print(f"\n[{item['provider']}] {item['status']}")
                print(item["content"] if item["status"] == "success" else item["error"])
    except httpx.HTTPError as error:
        print("Mini Agent 02 Backend 호출 실패:", error)
