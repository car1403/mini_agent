"""온도 센서와 명시적인 규칙으로 에어컨을 안전하게 제어합니다."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TemperatureReading(BaseModel):
    model_config = ConfigDict(extra="forbid")
    temperature_c: float = Field(ge=-40, le=80)


class AirConditionerState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    power: Literal["on", "off"] = "off"


def read_temperature(temperature_c: float) -> dict[str, float]:
    reading = TemperatureReading(temperature_c=temperature_c)
    return reading.model_dump()


def decide_action(temperature_c: float, current_power: str) -> Literal["turn_on", "turn_off", "keep"]:
    """27도 이상이면 켜고 23도 이하이면 끄며, 중간 구간에서는 현재 상태를 유지합니다."""
    if temperature_c >= 27 and current_power == "off":
        return "turn_on"
    if temperature_c <= 23 and current_power == "on":
        return "turn_off"
    return "keep"


def control_air_conditioner(action: str, state: AirConditionerState) -> dict[str, str]:
    if action == "turn_on":
        state.power = "on"
    elif action == "turn_off":
        state.power = "off"
    elif action != "keep":
        raise ValueError(f"허용되지 않은 동작입니다: {action}")
    return {"power": state.power, "action": action}


def run_workflow(temperatures: list[float]) -> list[dict]:
    state = AirConditionerState()
    trace = []
    for value in temperatures:
        sensor_result = read_temperature(value)
        action = decide_action(sensor_result["temperature_c"], state.power)
        control_result = control_air_conditioner(action, state)
        trace.append({"temperature_c": value, **control_result})
    return trace


if __name__ == "__main__":
    for item in run_workflow([26, 27, 25, 23, 24, 28]):
        print(item)
    print("\n이 예제는 판단 기준이 고정되어 있으므로 LLM Agent보다 규칙 기반 Workflow가 적합합니다.")
