"""Agent 행동 평가의 최소 예제."""

from dataclasses import dataclass


@dataclass
class Scenario:
    name: str
    expected_tool: str | None
    actual_tool: str | None
    expected_status: str
    actual_status: str


def evaluate(scenario: Scenario) -> dict:
    checks = {
        "tool_match": scenario.expected_tool == scenario.actual_tool,
        "status_match": scenario.expected_status == scenario.actual_status,
    }
    return {
        "name": scenario.name,
        "passed": all(checks.values()),
        "checks": checks,
    }


if __name__ == "__main__":
    result = evaluate(
        Scenario(
            name="날씨 질문",
            expected_tool="get_weather",
            actual_tool="get_weather",
            expected_status="completed",
            actual_status="completed",
        )
    )
    print(result)
