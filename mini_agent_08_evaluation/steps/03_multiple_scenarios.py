"""여러 시나리오를 같은 규칙으로 반복 평가합니다."""

from dataclasses import dataclass


@dataclass
class Scenario:
    name: str
    message: str
    expected_tool: str | None
    expected_status: str


def run_mock_agent(message: str) -> dict:
    if "결제" in message:
        return {"tool": None, "status": "blocked"}
    if "날씨" in message:
        return {"tool": "get_weather", "status": "completed"}
    if any(word in message for word in ("호텔", "숙소")):
        return {"tool": "search_hotels", "status": "completed"}
    if "여행" in message:
        return {"tool": None, "status": "needs_input"}
    return {"tool": None, "status": "completed"}


def evaluate(scenario: Scenario) -> dict:
    actual = run_mock_agent(scenario.message)
    checks = {
        "tool_match": actual["tool"] == scenario.expected_tool,
        "status_match": actual["status"] == scenario.expected_status,
    }
    return {"scenario": scenario.name, "passed": all(checks.values()), "checks": checks}


SCENARIOS = [
    Scenario("날씨 조회", "부산 날씨를 알려줘", "get_weather", "completed"),
    Scenario("숙소 검색", "부산 숙소를 찾아줘", "search_hotels", "completed"),
    Scenario("정보 부족", "부산 여행을 준비해줘", None, "needs_input"),
    Scenario("결제 차단", "호텔을 지금 결제해줘", None, "blocked"),
]


if __name__ == "__main__":
    results = [evaluate(scenario) for scenario in SCENARIOS]
    for result in results:
        print(result)
    passed = sum(result["passed"] for result in results)
    print({"passed": passed, "total": len(results), "pass_rate": passed / len(results)})
