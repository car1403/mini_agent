"""실제 Tool Call과 auto·none Tool Choice의 차이를 함께 관찰합니다."""

import httpx

from _tool_backend import print_help, select_tool


QUESTION = "내일 제주 날씨와 기온을 알려줘."


def print_decision(mode: str, decision: dict) -> None:
    print(f"\n===== tool_choice={mode} =====")
    print("1. Provider:", decision["provider"], decision["model"])
    print("2. 원본 Tool Call:", decision["raw_tool_call"])
    print("3. 정규화 Tool 이름:", decision["tool_name"])
    print("4. 정규화 arguments:", decision["arguments"])
    print("5. 누락 arguments:", decision["missing_arguments"])


if __name__ == "__main__":
    try:
        for tool_choice in ("auto", "none"):
            print_decision(tool_choice, select_tool(QUESTION, tool_choice=tool_choice))
        print("\nrequired는 불필요한 질문에도 Tool을 강제할 수 있어 Backend 또는 Streamlit에서 추가로 비교할 수 있습니다.")
        print("중요: 이 예제에서는 아직 Tool 함수를 실행하지 않았습니다.")
    except httpx.HTTPError as error:
        print_help(error)
