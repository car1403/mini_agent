"""User-only 방식과 System·User 역할 분리를 비교합니다."""

import httpx
from _llm_backend import generate_text, print_connection_help, print_result


MEETING = "민수는 금요일까지 API를 완성한다. 배포일은 다음 회의에서 정한다."
SYSTEM = "회의 기록 담당자입니다. 결정 사항과 할 일을 분리하고 미확정 내용은 제외하세요."


if __name__ == "__main__":
    try:
        print_result("User-only", generate_text("사용자 요청에 답하세요.", f"회의를 정리하세요. {MEETING}"))
        print_result("역할 분리", generate_text(SYSTEM, MEETING))
    except httpx.HTTPError as error:
        print_connection_help(error)
