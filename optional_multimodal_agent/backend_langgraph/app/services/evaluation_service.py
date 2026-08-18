from app.providers.factory import get_provider
from app.tools.definitions import TRAVEL_TOOL_DEFINITIONS


TOOL_SCENARIOS = [
    {"message": "8월 10일 부산 날씨를 알려줘", "expected_tool": "get_weather"},
    {
        "message": "8월 10일부터 12일까지 성인 2명 부산 숙소를 찾아줘",
        "expected_tool": "search_hotels",
    },
    {"message": "부산 여행을 한 문장으로 소개해줘", "expected_tool": None},
]


def evaluate_tool_selection(providers: list[str]) -> dict:
    results = []
    for provider_name in providers:
        rows = []
        try:
            provider = get_provider(provider_name)
            for scenario in TOOL_SCENARIOS:
                selected = provider.select_tool(
                    "필요한 경우에만 제공된 여행 Tool 중 하나를 선택하세요.",
                    scenario["message"],
                    TRAVEL_TOOL_DEFINITIONS,
                )
                rows.append(
                    {
                        **scenario,
                        "actual_tool": selected.tool_name,
                        "passed": selected.tool_name == scenario["expected_tool"],
                        "latency_ms": selected.latency_ms,
                    }
                )
            results.append(
                {
                    "provider": provider_name,
                    "model": provider.model,
                    "status": "completed",
                    "accuracy": sum(row["passed"] for row in rows) / len(rows),
                    "average_latency_ms": round(
                        sum(row["latency_ms"] for row in rows) / len(rows)
                    ),
                    "scenarios": rows,
                }
            )
        except Exception as error:
            results.append(
                {
                    "provider": provider_name,
                    "status": "failed",
                    "error": str(error),
                    "scenarios": rows,
                }
            )
    return {"scenario_set": "tool_selection", "results": results}
