"""입력·기대 결과·실제 결과를 가진 첫 평가 시나리오입니다."""

from dataclasses import dataclass


@dataclass
class Scenario:
    name: str
    message: str
    expected_tool: str | None
    expected_status: str


def run_mock_agent(message: str) -> dict:
    if "날씨" in message:
        return {"tool": "get_weather", "status": "completed"}
    return {"tool": None, "status": "completed"}


def evaluate(scenario: Scenario) -> dict:
    actual = run_mock_agent(scenario.message)
    checks = {
        "tool_match": actual["tool"] == scenario.expected_tool,
        "status_match": actual["status"] == scenario.expected_status,
    }
    return {
        "scenario": scenario.name,
        "passed": all(checks.values()),
        "expected": {
            "tool": scenario.expected_tool,
            "status": scenario.expected_status,
        },
        "actual": actual,
        "checks": checks,
    }


if __name__ == "__main__":
    scenario = Scenario(
        name="날씨 조회",
        message="부산 날씨를 알려줘",
        expected_tool="get_weather",
        expected_status="completed",
    )
    print(evaluate(scenario))
