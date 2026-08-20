"""필수 arguments가 부족할 때 값을 추측하지 않고 추가 질문을 반환합니다."""

import httpx

from _tool_backend import print_help, print_result, select_tool


QUESTIONS = ["숙소를 찾아줘.", "부산 숙소를 찾아줘.", "서울 관광지를 추천해 줘."]


if __name__ == "__main__":
    try:
        for question in QUESTIONS:
            print_result(question, select_tool(question))
    except httpx.HTTPError as error:
        print_help(error)
