"""현재 날씨와 미래 예보 질문에서 LLM이 서로 다른 Tool을 선택하는지 비교합니다."""

import httpx

from _tool_backend import print_help, print_result, select_tool


QUESTIONS = ["지금 부산에 비가 와?", "내일 부산에 비가 올까?"]


if __name__ == "__main__":
    try:
        for question in QUESTIONS:
            print(f"\n사용자 질문: {question}")
            print_result("Tool 선택 결과", select_tool(question))
    except httpx.HTTPError as error:
        print_help(error)
