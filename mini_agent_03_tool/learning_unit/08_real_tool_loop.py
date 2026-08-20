"""실제 Provider의 선택부터 Tool Result 기반 최종 답변까지 Trace를 출력합니다."""

import httpx

from _tool_backend import complete_loop, print_help


if __name__ == "__main__":
    try:
        result = complete_loop("오늘 부산 날씨와 기온을 알려줘.")
        for index, item in enumerate(result["trace"], start=1):
            print(f"\n{index}. {item['stage']}")
            print(item["data"])
        print("\n최종 답변:", result["final_answer"])
    except httpx.HTTPError as error:
        print_help(error)
