"""자유 응답과 TravelPlan Structured Output을 비교합니다."""

import httpx
from _llm_backend import generate_structured, generate_text, print_connection_help, print_result


MESSAGE = "부산 대중교통 2박 3일 여행을 제안해 주세요."


if __name__ == "__main__":
    try:
        print_result("자유 응답", generate_text("간결한 여행 계획을 작성하세요.", MESSAGE))
        print_result("Structured Output", generate_structured("travel_plan", "TravelPlan Schema에 맞춰 작성하세요.", MESSAGE))
    except httpx.HTTPError as error:
        print_connection_help(error)
