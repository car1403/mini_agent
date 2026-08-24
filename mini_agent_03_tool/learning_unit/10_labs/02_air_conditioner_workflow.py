"""Lab 02 — 온도 센서와 명시적인 규칙으로 에어컨을 안전하게 제어합니다.

학습 분류:
- 현재 성격: 규칙 기반 Workflow
- Agent 여부: 아니오
- 권장 방향: Agent가 필요 없는 반례로 유지
- 판단 근거: 온도와 현재 전원 상태만으로 다음 동작이 결정됩니다. LLM의 유연한
  판단보다 테스트 가능한 히스테리시스 규칙이 더 단순하고 안전합니다.

Backend 디렉터리 기준 역할:
- `schemas/`: TemperatureReading과 AirConditionerState가 센서값·장치 상태 계약입니다.
- `tools/`: read_temperature와 control_air_conditioner가 센서 조회·장치 제어 Tool입니다.
- `services/`: decide_action이 히스테리시스 업무 규칙을 적용합니다.
- `agents/`: 사용하지 않습니다. run_workflow는 판단 순서가 고정된 Workflow입니다.
- `routers/`: 이 파일에서는 `__main__` 실행부가 요청 진입점을 대신합니다.
- `providers/`: LLM 판단이 필요 없는 명시적 규칙 실습이므로 사용하지 않습니다.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# [schemas/] 센서가 반환할 수 있는 온도 범위를 검증하는 Schema입니다.
class TemperatureReading(BaseModel):
    model_config = ConfigDict(extra="forbid")
    temperature_c: float = Field(ge=-40, le=80)


# [schemas/] 에어컨의 허용된 전원 상태를 표현하는 Schema입니다.
class AirConditionerState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    power: Literal["on", "off"] = "off"


# [tools/] 센서 조회를 흉내 내고 검증된 측정값을 반환합니다.
def read_temperature(temperature_c: float) -> dict[str, float]:
    reading = TemperatureReading(temperature_c=temperature_c)
    return reading.model_dump()


# [services/] 온도와 현재 상태에 히스테리시스 업무 규칙을 적용합니다.
def decide_action(temperature_c: float, current_power: str) -> Literal["turn_on", "turn_off", "keep"]:
    """27도 이상이면 켜고 23도 이하이면 끄며, 중간 구간에서는 현재 상태를 유지합니다."""
    if temperature_c >= 27 and current_power == "off":
        return "turn_on"
    if temperature_c <= 23 and current_power == "on":
        return "turn_off"
    return "keep"


# [tools/] Service가 결정한 허용 동작만 장치 상태에 반영합니다.
def control_air_conditioner(action: str, state: AirConditionerState) -> dict[str, str]:
    if action == "turn_on":
        state.power = "on"
    elif action == "turn_off":
        state.power = "off"
    elif action != "keep":
        raise ValueError(f"허용되지 않은 동작입니다: {action}")
    return {"power": state.power, "action": action}


# [services/] 센서 조회 → 규칙 판단 → 장치 제어의 고정 Workflow를 반복합니다.
def run_workflow(temperatures: list[float]) -> list[dict]:
    state = AirConditionerState()
    trace = []
    for value in temperatures:
        sensor_result = read_temperature(value)
        action = decide_action(sensor_result["temperature_c"], state.power)
        control_result = control_air_conditioner(action, state)
        trace.append({"temperature_c": value, **control_result})
    return trace


# [routers/ 대체] API 요청 대신 온도 시계열을 입력해 Workflow 결과를 출력합니다.
if __name__ == "__main__":
    for item in run_workflow([26, 27, 25, 23, 24, 28]):
        print(item)
    print("\n이 예제는 판단 기준이 고정되어 있으므로 LLM Agent보다 규칙 기반 Workflow가 적합합니다.")
