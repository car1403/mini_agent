"""초보자용 결정적 규칙 평가 서비스."""

from time import perf_counter

from app.tools.travel_tools import select_tool


CORE_SCENARIOS = [
    {
        "name": "날씨 조회",
        "message": "부산 날씨를 알려줘",
        "expected_tool": "get_weather",
        "expected_status": "completed",
    },
    {
        "name": "숙소 검색",
        "message": "부산 숙소를 찾아줘",
        "expected_tool": "search_hotels",
        "expected_status": "completed",
    },
    {
        "name": "Tool 불필요",
        "message": "안녕하세요",
        "expected_tool": None,
        "expected_status": "completed",
    },
    {
        "name": "정보 부족",
        "message": "부산 여행을 준비해줘",
        "expected_tool": None,
        "expected_status": "needs_input",
    },
    {
        "name": "결제 차단",
        "message": "호텔을 지금 결제해줘",
        "expected_tool": None,
        "expected_status": "blocked",
    },
]


def _event(node: str, status: str, started: float, **details: object) -> dict:
    return {
        "node": node,
        "status": status,
        "duration_ms": round((perf_counter() - started) * 1000),
        **details,
    }


def run_mock_agent(message: str) -> dict:
    trace = []
    started = perf_counter()
    blocked = any(word in message for word in ("결제", "삭제", "다른 사용자"))
    trace.append(_event("check_policy", "completed", started, blocked=blocked))
    if blocked:
        return {"tool": None, "status": "blocked", "trace": trace}

    started = perf_counter()
    selection = select_tool(message)
    tool = selection["tool_name"]
    trace.append(_event("select_tool", "completed", started, tool=tool))

    if tool:
        status = "completed"
    elif "여행" in message:
        status = "needs_input"
    else:
        status = "completed"
    trace.append({"node": "finish", "status": status, "duration_ms": 0})
    return {"tool": tool, "status": status, "trace": trace}


def evaluate_scenario(scenario: dict) -> dict:
    actual = run_mock_agent(scenario["message"])
    checks = {
        "tool_match": actual["tool"] == scenario.get("expected_tool"),
        "status_match": actual["status"] == scenario["expected_status"],
    }
    passed = all(checks.values())
    failed_checks = [name for name, ok in checks.items() if not ok]
    trace = [
        *actual["trace"],
        {
            "node": "evaluate",
            "status": "completed" if passed else "failed",
            "duration_ms": 0,
            "error": None if passed else ", ".join(failed_checks),
        },
    ]
    return {
        "scenario": scenario["name"],
        "message": scenario["message"],
        "expected": {
            "tool": scenario.get("expected_tool"),
            "status": scenario["expected_status"],
        },
        "actual": {"tool": actual["tool"], "status": actual["status"]},
        "passed": passed,
        "checks": checks,
        "failed_checks": failed_checks,
        "trace": trace,
    }


def run_evaluation(scenarios: list[dict] | None = None) -> dict:
    selected = scenarios or CORE_SCENARIOS
    results = [evaluate_scenario(scenario) for scenario in selected]
    passed = sum(result["passed"] for result in results)
    total = len(results)
    return {
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 3) if total else 0.0,
        },
        "results": results,
    }
