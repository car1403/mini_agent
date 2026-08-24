"""상태에 따라 재질문·Tool 선택·종료를 결정하는 여행 준비 Agent입니다.

오늘과 미래 날짜에 따라 서로 다른 날씨 Tool을 선택하고, 날씨 근거를 확보한 뒤
관광지 Tool을 선택합니다. 읽기 전용이므로 상태 변경 Workflow와 승인 단계는 없습니다.
"""
from datetime import date, timedelta
from typing import Any
from app.repositories.lab_repository import lab_repository
from app.tools.lab_tools import execute_lab_tool

def run_travel_planning_agent(session_id: str, message: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """여러 사용자 Cycle에 걸쳐 도시와 날짜를 수집하고 두 조회 Tool을 조정합니다."""
    state = lab_repository.session(session_id, "travel")
    for city in ("서울", "부산", "제주"):
        if city in message: state["city"] = city
    today = date.today()
    if "오늘" in message: state["travel_date"] = today.isoformat()
    elif "내일" in message: state["travel_date"] = (today + timedelta(days=1)).isoformat()
    state.update({key: value for key, value in arguments.items() if key in {"city", "travel_date"}})
    missing = [key for key in ("city", "travel_date") if not state.get(key)]
    trace = [{"stage": "travel_agent_extraction", "data": state.copy()}]
    # 필요한 정보가 없으면 추측하지 않고 상태를 유지한 채 사용자 입력을 기다립니다.
    if missing: return {"status": "needs_clarification", "answer": f"다음 정보를 알려주세요: {', '.join(missing)}", "state": state.copy(), "trace": trace, "reason": "needs_user_input", "calls": []}
    target_date = date.fromisoformat(str(state["travel_date"])); weather_tool = "get_current_weather" if target_date == today else "get_weather_forecast"
    calls = [
        {"tool": weather_tool, "arguments": {"city": state["city"], "travel_date": target_date.isoformat()}},
        {"tool": "search_attractions", "arguments": {"city": state["city"]}},
    ]
    results: dict[str, Any] = {}
    for step, call in enumerate(calls, start=1):
        trace.append({"step": step, "stage": "agent_decision", "action": call["tool"]})
        execution = execute_lab_tool(call["tool"], call["arguments"])
        trace.append({"step": step, "stage": "tool_execution", "data": execution})
        if not execution["success"]:
            return {"status": "error", "answer": "여행 조회 Tool 실행에 실패했습니다.", "state": results, "trace": trace, "reason": "tool_error", "calls": calls[:step]}
        results[call["tool"]] = execution["data"]
    weather = results[weather_tool]
    attractions = results["search_attractions"]
    if not weather["found"] or not attractions["found"]:
        return {"status": "rejected", "answer": "해당 도시의 여행 정보를 찾지 못했습니다.", "state": results, "trace": trace, "reason": "no_evidence", "calls": calls}
    plan = {
        "city": state["city"], "travel_date": target_date.isoformat(),
        "weather": weather["weather"], "attractions": attractions["attractions"],
    }
    return {"status": "completed", "answer": f"{state['city']} 여행 준비 정보를 만들었습니다.", "state": plan, "trace": trace, "reason": "completed", "calls": calls}
