"""Routing 함수가 State를 읽고 다음 Node 이름을 선택합니다."""

from typing import Literal


def inspect_request(state: dict) -> dict:
    destination = "부산" if "부산" in state["message"] else None
    return {**state, "destination": destination}


def route(state: dict) -> Literal["ask_user", "create_plan"]:
    return "create_plan" if state.get("destination") else "ask_user"


if __name__ == "__main__":
    for message in ("부산 여행을 준비해줘", "여행을 준비해줘"):
        state = inspect_request({"message": message})
        print(message, "→", route(state), "→", state)

    print("Node는 값을 변경하고, Routing 함수는 경로만 선택합니다.")
