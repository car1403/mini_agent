"""Lab 07 — 날씨와 관광지 Tool을 사용해 여행 준비 정보를 만드는 Agent입니다.

학습 분류:
- 현재 성격: 재질문 + Multi-Tool 선택 + Tool Result 종합
- Agent 여부: 예
- 권장 방향: 제한된 반복 횟수를 가진 읽기 전용 Agent로 구현
- 판단 근거: Agent가 현재 상태와 Tool Result를 확인하면서 다음 Tool, 재질문 또는
  종료를 동적으로 선택합니다. 상태 변경 Tool이 없으므로 Agent 판단, 상태와 종료
  조건에 집중할 수 있습니다.

Backend 디렉터리 기준 역할:
- `schemas/`: TravelAgentState가 대화에서 수집한 값과 실행 상태 계약을 정의합니다.
- `tools/`: 현재 날씨, 미래 예보, 관광지 검색이라는 독립적인 읽기 Tool을 제공합니다.
- `agents/`: extract_request, choose_next_action과 run_agent_cycle이 다음 행동을 결정합니다.
- `services/`: build_travel_plan이 검증된 Tool Result만 이용해 최종 결과를 조립합니다.
- `providers/`: 실제 환경에서는 LLM이 요청 추출과 다음 Tool Call을 제안합니다.
- `routers/`: 이 파일에서는 `__main__` 실행부가 여러 사용자 메시지의 진입점입니다.

중요한 경계:
- Agent가 Tool Call을 제안해도 Backend Allowlist와 arguments 검증 후에만 실행합니다.
- 도시나 날짜가 없으면 임의로 추측하지 않고 사용자에게 재질문합니다.
- 한 번의 사용자 메시지마다 하나의 Agent Cycle을 실행하며, Cycle 내부에서는 필요한
  읽기 Tool을 최대 `max_steps` 범위에서 연속 호출할 수 있습니다.
"""

from datetime import date, timedelta
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


# [schemas/] 각 Tool의 arguments 계약입니다. 정의되지 않은 값은 허용하지 않습니다.
class WeatherInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str = Field(min_length=1)


class ForecastInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str = Field(min_length=1)
    travel_date: date


class AttractionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str = Field(min_length=1)


# [agents/] 대화 사이에 유지할 입력값, Tool Result와 Trace입니다.
class TravelAgentState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str | None = None
    travel_date: date | None = None
    weather_result: dict[str, Any] | None = None
    attraction_result: dict[str, Any] | None = None
    status: Literal["collecting", "running", "completed", "stopped"] = "collecting"
    trace: list[dict[str, Any]] = Field(default_factory=list)


# [학습용 저장소] 외부 API 대신 고정 데이터를 사용해 Agent 흐름을 재현합니다.
CURRENT_WEATHER = {
    "서울": {"condition": "맑음", "temperature_c": 27},
    "부산": {"condition": "비", "temperature_c": 23},
    "제주": {"condition": "바람", "temperature_c": 25},
}
ATTRACTIONS = {
    "서울": ["경복궁", "서울숲"],
    "부산": ["해운대", "감천문화마을"],
    "제주": ["성산일출봉", "비자림"],
}


# [tools/] 오늘의 날씨를 조회하는 읽기 전용 Tool입니다.
def get_current_weather(arguments: dict[str, Any]) -> dict[str, Any]:
    args = WeatherInput.model_validate(arguments)
    weather = CURRENT_WEATHER.get(args.city)
    if weather is None:
        return {"found": False, "city": args.city, "source": "mock-weather"}
    return {"found": True, "city": args.city, **weather, "source": "mock-weather"}


# [tools/] 미래 날짜의 예보를 조회하는 읽기 전용 Tool입니다.
def get_weather_forecast(arguments: dict[str, Any]) -> dict[str, Any]:
    args = ForecastInput.model_validate(arguments)
    if args.city not in CURRENT_WEATHER:
        return {"found": False, "city": args.city, "date": args.travel_date.isoformat(), "source": "mock-forecast"}
    # 학습용 Mock이므로 날짜에 따라 결과가 달라지는 것만 단순하게 표현합니다.
    condition = "비" if args.travel_date.day % 2 == 0 else "맑음"
    return {
        "found": True,
        "city": args.city,
        "date": args.travel_date.isoformat(),
        "condition": condition,
        "temperature_c": 22,
        "source": "mock-forecast",
    }


# [tools/] 도시의 관광지를 검색하는 읽기 전용 Tool입니다.
def search_attractions(arguments: dict[str, Any]) -> dict[str, Any]:
    args = AttractionInput.model_validate(arguments)
    items = ATTRACTIONS.get(args.city, [])
    return {"found": bool(items), "city": args.city, "items": items, "source": "mock-attractions"}


# [tools/] Tool 이름, 입력 Schema와 실행 함수를 함께 보관하는 Backend Allowlist입니다.
TOOL_REGISTRY = {
    "get_current_weather": (WeatherInput, get_current_weather),
    "get_weather_forecast": (ForecastInput, get_weather_forecast),
    "search_attractions": (AttractionInput, search_attractions),
}


def execute_allowed_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Agent의 제안을 신뢰하지 않고 등록 여부와 arguments를 다시 검증합니다."""
    tool_spec = TOOL_REGISTRY.get(tool_name)
    if tool_spec is None:
        return {"success": False, "error": {"code": "TOOL_NOT_ALLOWED"}}
    input_model, function = tool_spec
    try:
        validated = input_model.model_validate(arguments)
        return {"success": True, "data": function(validated.model_dump(mode="json"))}
    except ValidationError as error:
        return {"success": False, "error": {"code": "VALIDATION_ERROR", "details": error.errors()}}


# [agents/] 실제 Provider의 Structured Output을 흉내 내어 도시와 날짜를 추출합니다.
def extract_request(message: str, today: date) -> dict[str, Any]:
    extracted: dict[str, Any] = {}
    for city in CURRENT_WEATHER:
        if city in message:
            extracted["city"] = city
            break
    if "오늘" in message:
        extracted["travel_date"] = today
    elif "내일" in message:
        extracted["travel_date"] = today + timedelta(days=1)
    elif "이번 주말" in message or "주말" in message:
        days_until_saturday = (5 - today.weekday()) % 7
        extracted["travel_date"] = today + timedelta(days=days_until_saturday)
    return extracted


# [agents/] 현재 상태를 보고 재질문, Tool Call 또는 종료 중 다음 행동을 선택합니다.
def choose_next_action(state: TravelAgentState, today: date) -> str:
    if state.city is None or state.travel_date is None:
        return "ask_clarification"
    if state.weather_result is None:
        return "get_current_weather" if state.travel_date == today else "get_weather_forecast"
    if state.attraction_result is None:
        return "search_attractions"
    return "finish"


# [services/] Tool Result에 있는 사실만 이용해 결정적으로 최종 여행 정보를 만듭니다.
def build_travel_plan(state: TravelAgentState) -> dict[str, Any]:
    weather = state.weather_result or {}
    attractions = state.attraction_result or {}
    preparation = ["편한 신발"]
    if weather.get("condition") == "비":
        preparation.append("우산")
    if weather.get("temperature_c", 100) <= 23:
        preparation.append("얇은 겉옷")
    return {
        "city": state.city,
        "travel_date": state.travel_date.isoformat() if state.travel_date else None,
        "weather": weather,
        "attractions": attractions.get("items", []),
        "preparation": preparation,
    }


# [agents/] 한 사용자 입력을 처리하고 재질문 또는 완료까지 진행하는 Agent Cycle입니다.
def run_agent_cycle(
    state: TravelAgentState,
    user_message: str,
    today: date,
    max_steps: int = 4,
) -> dict[str, Any]:
    extracted = extract_request(user_message, today)
    if "city" in extracted and extracted["city"] != state.city:
        # 목적지가 바뀌면 이전 목적지의 Tool Result를 재사용하지 않습니다.
        state.weather_result = None
        state.attraction_result = None
    if "travel_date" in extracted and extracted["travel_date"] != state.travel_date:
        state.weather_result = None
    for key, value in extracted.items():
        setattr(state, key, value)
    state.trace.append({"stage": "extract_request", "data": extracted})

    for step in range(1, max_steps + 1):
        action = choose_next_action(state, today)
        state.trace.append({"step": step, "stage": "agent_decision", "action": action})

        if action == "ask_clarification":
            missing = [name for name in ("city", "travel_date") if getattr(state, name) is None]
            labels = {"city": "여행 도시", "travel_date": "여행 날짜"}
            state.status = "collecting"
            return {
                "status": "needs_clarification",
                "missing_arguments": missing,
                "follow_up_question": f"{', '.join(labels[name] for name in missing)}을(를) 알려주세요.",
                "termination_reason": "needs_user_input",
                "trace": state.trace.copy(),
            }

        if action == "finish":
            state.status = "completed"
            return {
                "status": "completed",
                "plan": build_travel_plan(state),
                "termination_reason": "completed",
                "trace": state.trace.copy(),
            }

        if action == "get_current_weather":
            arguments = {"city": state.city}
        elif action == "get_weather_forecast":
            arguments = {"city": state.city, "travel_date": state.travel_date}
        else:
            arguments = {"city": state.city}

        execution = execute_allowed_tool(action, arguments)
        state.trace.append({"step": step, "stage": "tool_result", "tool": action, "data": execution})
        if not execution["success"]:
            state.status = "stopped"
            return {
                "status": "error",
                "error": execution["error"],
                "termination_reason": "tool_error",
                "trace": state.trace.copy(),
            }
        if action in ("get_current_weather", "get_weather_forecast"):
            state.weather_result = execution["data"]
        else:
            state.attraction_result = execution["data"]

    state.status = "stopped"
    return {
        "status": "stopped",
        "termination_reason": "max_steps_exceeded",
        "trace": state.trace.copy(),
    }


# [routers/ 대체] 첫 Cycle의 재질문과 두 번째 Cycle의 Multi-Tool 실행을 확인합니다.
if __name__ == "__main__":
    reference_date = date(2026, 8, 21)
    agent_state = TravelAgentState()
    for message in ("이번 주말 여행 준비물을 추천해 줘", "부산으로 갈게"):
        print(f"\n사용자: {message}")
        print(run_agent_cycle(agent_state, message, reference_date))

